"""
local_fallback_client.py
--------------------------
A local, dependency-free stand-in for `hindsight_client.Hindsight`.

It implements the same four calls the agent uses — create_bank, retain,
recall, reflect — with the same argument names and the same shape of
return value (objects with .results / .text), so meeting_prep_agent.py
is written *once* against this interface and works unmodified against
the real Hindsight Cloud client.

This is intentionally simple (keyword overlap instead of embeddings,
templated summaries instead of an LLM call) — it exists only so the
agent's branching logic can be demoed and tested without network access
or API credits. The real Hindsight backend is what should be used for
the hackathon submission itself.
"""

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

STORE_PATH = os.path.join(os.path.dirname(__file__), "local_hindsight_fallback.json")


@dataclass
class MemoryItem:
    content: str
    context: Optional[str]
    timestamp: str


@dataclass
class RecallResult:
    results: List["RecallHit"]


@dataclass
class RecallHit:
    text: str
    context: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass
class ReflectResult:
    text: str


def _tokenize(text: str):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class LocalFallbackClient:
    def __init__(self, store_path: str = STORE_PATH):
        self.store_path = store_path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.store_path):
            with open(self.store_path, "r") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        with open(self.store_path, "w") as f:
            json.dump(self._data, f, indent=2)

    # ---- Hindsight-compatible interface ----

    def create_bank(self, bank_id: str, name: str = None):
        self._data.setdefault(bank_id, {"name": name or bank_id, "items": []})
        self._save()
        return {"bank_id": bank_id, "name": name}

    def retain(self, bank_id: str, content: str, context: str = None, timestamp: str = None):
        self._data.setdefault(bank_id, {"name": bank_id, "items": []})
        self._data[bank_id]["items"].append(
            {
                "content": content,
                "context": context,
                "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
            }
        )
        self._save()
        return {"status": "stored"}

    def recall(self, bank_id: str, query: str) -> RecallResult:
        items = self._data.get(bank_id, {}).get("items", [])
        q_tokens = _tokenize(query)

        scored = []
        for item in items:
            overlap = len(q_tokens & _tokenize(item["content"]))
            scored.append((overlap, item))
        scored.sort(key=lambda pair: (pair[0], pair[1]["timestamp"]), reverse=True)

        hits = [
            RecallHit(text=item["content"], context=item["context"], timestamp=item["timestamp"])
            for _, item in scored
        ]
        return RecallResult(results=hits)

    def reflect(self, bank_id: str, query: str) -> ReflectResult:
        items = sorted(
            self._data.get(bank_id, {}).get("items", []), key=lambda i: i["timestamp"]
        )

        if not items:
            return ReflectResult(
                text="No history on file for this contact yet — this will be your first meeting."
            )

        notes = [i for i in items if i["context"] == "meeting_notes"]
        commitments = [i for i in items if i["context"] == "commitment"]
        follow_ups = [i for i in items if i["context"] == "follow_up"]

        lines = [f"MEETING BRIEF — {len(notes)} prior meeting(s) on file.", ""]

        lines.append("Timeline:")
        for n in notes:
            lines.append(f"  [{n['timestamp'][:10]}] {n['content']}")

        if commitments:
            lines.append("")
            lines.append("Commitments made across all meetings:")
            for c in commitments:
                lines.append(f"  - {c['content']}")

        if follow_ups:
            lines.append("")
            lines.append("\u26a0 STILL OPEN — raise these before anything new:")
            for f in follow_ups:
                lines.append(f"  - {f['content']}")
        else:
            lines.append("")
            lines.append("No open follow-ups on file.")

        return ReflectResult(text="\n".join(lines))
