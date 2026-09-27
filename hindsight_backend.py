"""
hindsight_backend.py
----------------------
Picks the memory backend the rest of the app talks to.

- If HINDSIGHT_API_KEY is set AND the `hindsight-client` package is
  installed, we use the real Hindsight Cloud client. This is the actual
  hackathon-required backend — see https://hindsight.vectorize.io/
- Otherwise, we fall back to a small local implementation with the exact
  same method signatures (create_bank / retain / recall / reflect), so
  you can develop and demo the agent's *logic* without spending API
  credits, then flip it on for real with zero code changes elsewhere.

To use your real Hindsight Cloud key:

    export HINDSIGHT_API_KEY="your-api-key"
    export HINDSIGHT_BASE_URL="https://api.hindsight.vectorize.io"   # default
    pip install hindsight-client

That's it — meeting_prep_agent.py never changes.
"""

import os


def get_client():
    api_key = os.environ.get("HINDSIGHT_API_KEY")
    base_url = os.environ.get("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")

    if api_key:
        try:
            from hindsight_client import Hindsight

            print(f"[hindsight] Using real Hindsight Cloud at {base_url}")
            return Hindsight(base_url=base_url, api_key=api_key)
        except ImportError:
            print(
                "[hindsight] HINDSIGHT_API_KEY is set but the 'hindsight-client' "
                "package isn't installed.\n"
                "            Run: pip install hindsight-client\n"
                "            Falling back to local memory for now.\n"
            )

    print("[hindsight] No HINDSIGHT_API_KEY found — using local fallback memory.")
    from local_fallback_client import LocalFallbackClient

    return LocalFallbackClient()
