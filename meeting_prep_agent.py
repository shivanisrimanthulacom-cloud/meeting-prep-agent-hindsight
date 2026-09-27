"""
meeting_prep_agent.py
------------------------
The agent itself. Written only against the Hindsight-style interface
(create_bank / retain / recall / reflect) — it doesn't know or care
whether hindsight_backend handed it the real Hindsight Cloud client or
the local fallback.

Design choice: one Hindsight memory bank PER CONTACT. That mirrors how
a person actually thinks about "my relationship with Jordan" vs. "my
relationship with Priya" — each contact's memory bank builds its own
history, and recall/reflect are automatically scoped to that person.
"""

import re
from datetime import datetime, timezone
from typing import List, Optional

from hindsight_backend import get_client


def _bank_id_for_contact(contact_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", contact_name.strip().lower()).strip("-")
    return f"contact-{slug}"


class MeetingPrepAgent:
    def __init__(self):
        self.client = get_client()
        self._known_banks = set()

    def _ensure_bank(self, bank_id: str, display_name: str) -> None:
        if bank_id in self._known_banks:
            return
        try:
            self.client.create_bank(bank_id=bank_id, name=display_name)
        except Exception:
            pass  # bank likely already exists — fine either way
        self._known_banks.add(bank_id)

    def log_meeting(
        self,
        contact_name: str,
        company: str,
        notes: str,
        commitments: Optional[List[str]] = None,
        follow_ups_needed: Optional[List[str]] = None,
        meeting_date: Optional[str] = None,
    ) -> None:
        """Record a meeting that just happened."""
        bank_id = _bank_id_for_contact(contact_name)
        self._ensure_bank(bank_id, f"{contact_name} ({company})")

        timestamp = meeting_date or datetime.now(timezone.utc).isoformat()

        self.client.retain(
            bank_id=bank_id,
            content=f"Meeting with {contact_name} at {company}: {notes}",
            context="meeting_notes",
            timestamp=timestamp,
        )

        for commitment in commitments or []:
            self.client.retain(
                bank_id=bank_id,
                content=f"Commitment made: {commitment}",
                context="commitment",
                timestamp=timestamp,
            )

        for follow_up in follow_ups_needed or []:
            self.client.retain(
                bank_id=bank_id,
                content=f"Open follow-up: {follow_up}",
                context="follow_up",
                timestamp=timestamp,
            )

    def resolve_follow_up(self, contact_name: str, description: str) -> None:
        """Call this once a previously-open follow-up is actually handled."""
        bank_id = _bank_id_for_contact(contact_name)
        self._ensure_bank(bank_id, contact_name)
        self.client.retain(
            bank_id=bank_id,
            content=f"Resolved follow-up: {description}",
            context="meeting_notes",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def prep_brief(self, contact_name: str) -> str:
        """The main event: synthesize everything on file into a pre-meeting brief."""
        bank_id = _bank_id_for_contact(contact_name)
        self._ensure_bank(bank_id, contact_name)

        response = self.client.reflect(
            bank_id=bank_id,
            query=(
                f"Prepare me for my next meeting with {contact_name}. "
                "Summarize everything discussed so far, list every commitment "
                "made and whether it's been fulfilled, and flag any follow-ups "
                "that are still open."
            ),
        )
        return response.text

    def search_history(self, contact_name: str, query: str):
        """Ad-hoc recall, e.g. 'what did they say about pricing?'"""
        bank_id = _bank_id_for_contact(contact_name)
        self._ensure_bank(bank_id, contact_name)
        result = self.client.recall(bank_id=bank_id, query=query)
        return result.results
