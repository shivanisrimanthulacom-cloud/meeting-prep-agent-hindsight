"""
cli.py
--------
A real command-line tool, not just a demo script. Use this the way you'd
actually use the agent day to day.

Examples:

    # After a meeting:
    python3 cli.py log \\
        --contact "Jordan Lee" --company "Meridian Health" \\
        --notes "Discussed API integration timeline" \\
        --commitment "Send security whitepaper by Friday" \\
        --follow-up "Confirm data residency requirements"

    # Before your next meeting with them:
    python3 cli.py prep --contact "Jordan Lee"

    # Ad-hoc question over their history:
    python3 cli.py ask --contact "Jordan Lee" --query "what did they say about pricing?"
"""

import argparse

from meeting_prep_agent import MeetingPrepAgent


def main():
    parser = argparse.ArgumentParser(description="Meeting Prep Agent (Hindsight-powered)")
    sub = parser.add_subparsers(dest="command", required=True)

    log_p = sub.add_parser("log", help="Log a meeting that just happened")
    log_p.add_argument("--contact", required=True)
    log_p.add_argument("--company", required=True)
    log_p.add_argument("--notes", required=True)
    log_p.add_argument("--commitment", action="append", default=[], dest="commitments")
    log_p.add_argument("--follow-up", action="append", default=[], dest="follow_ups")
    log_p.add_argument("--date", default=None, help="ISO timestamp; defaults to now")

    prep_p = sub.add_parser("prep", help="Get a pre-meeting brief for a contact")
    prep_p.add_argument("--contact", required=True)

    ask_p = sub.add_parser("ask", help="Ask an ad-hoc question about a contact's history")
    ask_p.add_argument("--contact", required=True)
    ask_p.add_argument("--query", required=True)

    resolve_p = sub.add_parser("resolve", help="Mark a follow-up as handled")
    resolve_p.add_argument("--contact", required=True)
    resolve_p.add_argument("--description", required=True)

    args = parser.parse_args()
    agent = MeetingPrepAgent()

    if args.command == "log":
        agent.log_meeting(
            contact_name=args.contact,
            company=args.company,
            notes=args.notes,
            commitments=args.commitments,
            follow_ups_needed=args.follow_ups,
            meeting_date=args.date,
        )
        print(f"Logged meeting with {args.contact}.")

    elif args.command == "prep":
        print(agent.prep_brief(args.contact))

    elif args.command == "ask":
        hits = agent.search_history(args.contact, args.query)
        if not hits:
            print("Nothing relevant found.")
        for h in hits:
            ts = getattr(h, "timestamp", None) or getattr(h, "created_at", None) or ""
            prefix = f"[{str(ts)[:10]}] " if ts else ""
            print(f"- {prefix}{h.text}")

    elif args.command == "resolve":
        agent.resolve_follow_up(args.contact, args.description)
        print(f"Marked as resolved for {args.contact}.")


if __name__ == "__main__":
    main()
