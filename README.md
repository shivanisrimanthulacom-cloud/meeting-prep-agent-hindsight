# Meeting Prep Agent — built on Hindsight

A working agent for the Vectorize Hindsight hackathon (Product & Strategy
track). It remembers every past meeting with a contact — what was
discussed, what was promised, what's still unresolved — and generates a
pre-meeting brief automatically before you walk into the next one.

## The story (this is the demo)

1. **First meeting with a new contact** — brief comes back empty. Nothing
   to prep, because nothing has happened yet.
2. **Second meeting** — a promise gets broken (whitepaper never sent) and
   a competitor enters the picture.
3. **Third meeting** — *before it even happens*, the brief generated from
   memory surfaces the broken promise and the competitor threat, unprompted.
   That's the moment that sells the project: the agent didn't just store
   text, it changed what it told you because of what happened weeks ago.

Run `python3 demo.py` to see this end to end.

## Architecture — why Hindsight is the star, not a feature

| File | Role |
|---|---|
| `hindsight_backend.py` | Picks the real Hindsight Cloud client if `HINDSIGHT_API_KEY` is set, else a local fallback with an identical interface |
| `local_fallback_client.py` | Drop-in stand-in for offline development/testing only — not the hackathon submission path |
| `meeting_prep_agent.py` | The agent: one **Hindsight memory bank per contact**, using `retain` / `recall` / `reflect` |
| `cli.py` | Real command-line tool for day-to-day use |
| `demo.py` | The scripted three-meeting story above |

**One memory bank per contact** is the key design choice: it mirrors how
you actually think about relationships ("what do I know about Jordan?"
vs. "what do I know about Priya?"), and it means `recall`/`reflect` are
automatically scoped to the right person with no manual filtering.

Every meeting produces three kinds of memory, written with `client.retain`:
- `context="meeting_notes"` — what was discussed
- `context="commitment"` — what either side promised
- `context="follow_up"` — what's still open

The pre-meeting brief is a single `client.reflect(...)` call asking
Hindsight to summarize the relationship, list every commitment and
whether it's been honored, and flag open follow-ups. On the real
Hindsight backend this is genuine LLM synthesis over the retained
memories, not string templating.

## Setup with your real Hindsight Cloud key

```bash
pip install hindsight-client

export HINDSIGHT_API_KEY="your-api-key"
export HINDSIGHT_BASE_URL="https://api.hindsight.vectorize.io"   # default, can omit

python3 demo.py
```

No code changes needed — `hindsight_backend.py` detects the key and
switches from the local fallback to the real Hindsight client
automatically. (Remember to apply promo code `MEMHACK99` in the billing
section of Hindsight Cloud after registering, per the hackathon doc.)

## Day-to-day CLI usage

```bash
# After a meeting:
python3 cli.py log \
  --contact "Jordan Lee" --company "Meridian Health" \
  --notes "Discussed API integration timeline" \
  --commitment "Send security whitepaper by Friday" \
  --follow-up "Confirm data residency requirements"

# Before your next meeting with them:
python3 cli.py prep --contact "Jordan Lee"

# Ad-hoc question over their history:
python3 cli.py ask --contact "Jordan Lee" --query "what did they say about pricing?"

# Once a follow-up is actually handled:
python3 cli.py resolve --contact "Jordan Lee" --description "Sent the whitepaper"
```

## Mapping to the judging criteria

- **Innovation (30%)** — goes beyond a chatbot: it's a proactive brief
  generated *before* you ask, built from commitments and follow-ups
  extracted from raw meeting notes.
- **Use of Hindsight Memory (25%)** — memory isn't a side feature, it's
  the entire product. Remove Hindsight and there's no brief to generate.
- **Technical Implementation (20%)** — clean separation between the
  Hindsight-backed agent logic and the backend it happens to be talking
  to; per-contact bank isolation; graceful handling when a bank doesn't
  exist yet.
- **User Experience (15%)** — a two-command workflow (`log`, `prep`)
  that matches how people already think about meeting prep.
- **Real-world Impact (10%)** — every account exec, customer success
  manager, and BD lead has this exact pain point.

## Still needed for submission (per the hackathon doc)

- [ ] GitHub repo (push this project)
- [ ] Demo video walking through `demo.py`'s three-meeting story
- [ ] Live demo to judges
- [ ] Article / social post / video per the content guide
- [ ] Short written explanation of how Hindsight memory is used (the
      "Architecture" section above is a good starting draft)
