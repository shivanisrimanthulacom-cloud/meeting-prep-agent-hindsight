"""
demo.py
--------
The hackathon demo script. Tells one story:

  Meeting 1: nothing on file, brief is empty.
  Meeting 2: a promise gets broken and a competitor enters the picture.
  Meeting 3: the brief on file BEFORE this meeting flags the broken
             promise and the competitor threat automatically —
             this is the moment that makes memory the star of the demo.

Run with:  python3 demo.py
"""

from meeting_prep_agent import MeetingPrepAgent


def line(title):
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def main():
    agent = MeetingPrepAgent()
    contact = "Jordan Lee"
    company = "Meridian Health"

    line(f"BEFORE ANY MEETINGS: prep brief for {contact}")
    print(agent.prep_brief(contact))

    line("MEETING 1 — Jan 10, 2026 (intro call)")
    agent.log_meeting(
        contact_name=contact,
        company=company,
        notes=(
            "Intro call. Jordan is evaluating us for a partnership integration "
            "into their patient portal. Wants to see our security posture "
            "before going further."
        ),
        commitments=["Send technical security whitepaper by Jan 17"],
        meeting_date="2026-01-10T15:00:00Z",
    )
    print("Meeting logged.")

    line(f"PREP BRIEF before Meeting 2 (generated from Meeting 1 alone)")
    print(agent.prep_brief(contact))

    line("MEETING 2 — Jan 24, 2026 (follow-up call)")
    agent.log_meeting(
        contact_name=contact,
        company=company,
        notes=(
            "Follow-up call. We never sent the security whitepaper from the "
            "last meeting — Jordan raised it directly and seemed frustrated. "
            "Jordan also mentioned they're in parallel talks with a competitor, "
            "HealthLinkAI, who already sent their security docs."
        ),
        commitments=[
            "Send security whitepaper AND a case study by Jan 27, no more delays"
        ],
        follow_ups_needed=[
            "Confirm with Jordan that HealthLinkAI hasn't been given an exclusivity window"
        ],
        meeting_date="2026-01-24T15:00:00Z",
    )
    print("Meeting logged.")

    line("PREP BRIEF before Meeting 3 — THIS is the memory payoff")
    print(agent.prep_brief(contact))
    print(
        "\n>>> Notice: the agent surfaces the broken promise and the competitor\n"
        ">>> threat from a meeting two weeks ago, unprompted, before you even\n"
        ">>> walk into the room."
    )

    line("Ad-hoc recall: 'what has Jordan said about competitors?'")
    hits = agent.search_history(contact, "competitor pricing exclusivity")

    # Hindsight can return several near-duplicate phrasings of the same
    # underlying fact. For a clean demo, show only the first few distinct
    # ones rather than every raw variant.
    seen = set()
    shown = 0
    for h in hits:
        key = h.text.strip().lower()[:60]  # dedupe on a normalized prefix
        if key in seen:
            continue
        seen.add(key)

        ts = getattr(h, "timestamp", None) or getattr(h, "created_at", None) or ""
        prefix = f"[{str(ts)[:10]}] " if ts else ""
        print(f"- {prefix}{h.text}")

        shown += 1
        if shown >= 5:
            break


if __name__ == "__main__":
    main()
