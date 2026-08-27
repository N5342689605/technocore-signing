#!/usr/bin/env python3
"""
sweep_probe.py
==============
Measure technocore.chat's server-side single-line sweep from the outside.

How it works
------------
When a signature fails to verify, the server returns 403 along with the exact
string the signature should have covered. That string is the text AFTER the
sweep has been applied. Therefore:

    post with a garbage signature -> read the 403 body -> you have observed
    the server's sweep

No valid signature is needed. No private key is needed. The sweep is fully
observable from outside.

Usage
-----
    python sweep_probe.py p-<throwaway room name>

Nothing is stored (a 403 is not recorded as a write), but requests are spaced
out to stay clear of the rate limiter.
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "https://technocore.chat"
# A well-formed dummy did:key. No private key is involved.
DUMMY_DID = "did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK"
DELAY = 0.6  # seconds, to stay clear of the rate limiter

# (label, character, Unicode category, does THIS implementation sweep it?)
PROBES = [
    ("U+0009 TAB",                "\u0009", "Cc", True),
    ("U+000A LINE FEED",          "\u000a", "Cc", True),
    ("U+000D CARRIAGE RETURN",    "\u000d", "Cc", True),
    ("U+001B ESCAPE",             "\u001b", "Cc", True),
    ("U+007F DELETE",             "\u007f", "Cc", True),
    ("U+0085 NEXT LINE",          "\u0085", "Cc", True),
    ("U+00AD SOFT HYPHEN",        "\u00ad", "Cf", True),
    ("U+200B ZERO WIDTH SPACE",   "\u200b", "Cf", True),
    ("U+200D ZWJ",                "\u200d", "Cf", True),
    ("U+202E RLO",                "\u202e", "Cf", True),
    ("U+FEFF BOM",                "\ufeff", "Cf", True),
    ("U+2028 LINE SEPARATOR",     "\u2028", "Zl", True),   # inferred, not documented
    ("U+2029 PARAGRAPH SEP",      "\u2029", "Zp", True),   # inferred, not documented
    # Co (private use). The first 18-probe run omitted this category entirely and
    # therefore reported a sweep set that was a strict subset of the real one.
    # Cs (surrogates) cannot be probed at all: they are not valid UTF-8, so they
    # never survive the request. The server declares them swept.
    ("U+E000 PRIVATE USE FIRST",  "\ue000", "Co", True),
    ("U+F8FF PRIVATE USE LAST",   "\uf8ff", "Co", True),
    ("U+F0000 PLANE-15 PUA",      "\U000f0000", "Co", True),
    ("U+10FFFD PLANE-16 PUA",     "\U0010fffd", "Co", True),
    ("U+E0001 LANGUAGE TAG",      "\U000e0001", "Cf", True),
    ("U+2060 WORD JOINER",        "\u2060", "Cf", True),
    ("U+061C ARABIC LETTER MARK", "\u061c", "Cf", True),
    ("U+00A0 NBSP",               "\u00a0", "Zs", False),
    ("U+3000 IDEOGRAPHIC SPACE",  "\u3000", "Zs", False),
    ("U+2003 EM SPACE",           "\u2003", "Zs", False),
    ("U+FE0F VARIATION SEL-16",   "\ufe0f", "Mn", False),
    ("U+0301 COMBINING ACUTE",    "\u0301", "Mn", False),
]

LEFT, RIGHT = "A", "B"  # markers bracketing the probe character


def probe(room: str, ch: str, nonce: int) -> tuple[str | None, str]:
    """Post one probe character; return the post-sweep text from the 403 body."""
    text = f"{LEFT}{ch}{RIGHT}"
    fake_sig = base64.urlsafe_b64encode(os.urandom(64)).decode().rstrip("=")
    body = json.dumps(
        {"did": DUMMY_DID, "sig": fake_sig, "nonce": nonce, "text": text}
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/r/{room}",
        data=body,
        headers={"Content-Type": "application/json",
                 "User-Agent": "sweep-probe/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return None, f"UNEXPECTED: HTTP {r.status} - the garbage signature verified"
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        if e.code == 429:
            return None, f"429 rate limited: {raw.strip()[:120]}"
        if e.code != 403:
            return None, f"HTTP {e.code}: {raw.strip()[:120]}"
        # The last non-empty line is  <room>|<nonce>|<post-sweep text>
        lines = [ln for ln in raw.splitlines() if ln.strip()]
        if not lines:
            return None, "403 with an empty body"
        payload = lines[-1]
        prefix = f"{room}|{nonce}|"
        if not payload.startswith(prefix):
            return None, f"unexpected body format: {payload[:80]!r}"
        return payload[len(prefix):], "ok"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"network error: {e}"


def main() -> None:
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if len(sys.argv) != 2:
        sys.exit("usage: python sweep_probe.py p-<throwaway room name>")
    room = sys.argv[1]

    print(f"target : {BASE_URL}/r/{room}")
    print(f"probes : {len(PROBES)}   (about {int(len(PROBES)*DELAY)+5}s)")
    print("=" * 78)
    print(f"{'character':28} {'cat':4} {'server':12} {'ours':12} {'agree'}")
    print("-" * 78)

    nonce = int(time.time() * 1000)
    rows, mismatches = [], []

    for name, ch, cat, ours_sweeps in PROBES:
        nonce += 1
        swept, status = probe(room, ch, nonce)
        if swept is None:
            print(f"{name:28} {cat:4} -- {status}")
            rows.append((name, ch, cat, None, ours_sweeps))
            time.sleep(DELAY)
            continue

        # What survived between the markers
        if swept.startswith(LEFT) and swept.endswith(RIGHT):
            middle = swept[len(LEFT):-len(RIGHT)]
        else:
            middle = swept
        server_sweeps = (middle == " ")
        kept = (middle == ch)

        if server_sweeps:
            server_desc = "-> space"
        elif kept:
            server_desc = "unchanged"
        elif middle == "":
            server_desc = "deleted"
        else:
            server_desc = f"-> {middle!r}"

        agree = (server_sweeps == ours_sweeps)
        print(f"{name:28} {cat:4} {server_desc:12} "
              f"{'-> space' if ours_sweeps else 'unchanged':12} "
              f"{'ok' if agree else '** MISMATCH'}")
        rows.append((name, ch, cat, server_desc, ours_sweeps))
        if not agree:
            mismatches.append((name, cat, server_desc, ours_sweeps))
        time.sleep(DELAY)

    print("=" * 78)
    if mismatches:
        print(f"\n** {len(mismatches)} mismatch(es). The local sweep needs fixing.\n")
        for name, cat, server_desc, ours in mismatches:
            print(f"  {name} ({cat}): server {server_desc}, "
                  f"ours {'-> space' if ours else 'unchanged'}")
        print("\n  If the server sweeps a character and you do not, signatures over")
        print("  text containing it will fail to verify. If you sweep one the server")
        print("  leaves alone, you send different bytes than you signed. Either way,")
        print("  the write is rejected. Both directions need fixing.")
    else:
        print("\nAll probes agree. The local sweep matches the server.")

    print(f"\nNote: observed by bracketing each character as {LEFT}...{RIGHT}. "
          "The server's 403 body is the only source of truth here.")


if __name__ == "__main__":
    main()
