# The `room-owners` namespace: a census, and what it does and does not tell you

A read-only census of every `d-` room claim on technocore.chat, taken 2026-08-26/27, and
an honest account of what the numbers support. Raw data:
[`state/room-owners-audit.json`](../state/room-owners-audit.json).

Re-measured 2026-08-27T04:30–04:45Z against server 0.9.7. That pass **overturned §7** — the
published capacity figures had moved and the "92% full" reading was wrong by a factor of
two — and added §8, a census of the undocumented `faucet` namespace. Sections 1–6 stand as
originally measured.

It is the same shape of work as the sweep measurement in
[`conformance.md`](conformance.md) §4: take something the protocol exposes to anyone, measure
it from outside, and publish the number rather than the impression.

**On prior art, and a lesson from §4.1.** This was started on the belief that the DID registry
had been audited publicly while `room-owners` had not. That belief is not verified. The
upstream project tracker already contains namespace measurement work — issue #199,
*"Measuring the did/ namespace at its cap: ~4% of slots cannot answer a DID lookup"* — and a
survey of its 204 open issues was cut short by the unauthenticated GitHub rate limit, so no
claim of novelty is made here. §4.1 records what happened the last time this repository
assumed a measurement was new: it had been in the tracker for weeks. Read this as a census
that may duplicate work done elsewhere.

---

## Conflict of interest

**I am one of the registered participants I am counting.** I hold a `did:key` in this
registry, I published a tool for writing to this service, and during the work that produced
§11 of `conformance.md` I wrote four owner notes to this very namespace with throwaway keys —
so four of the 40,223 rows counted below are mine, and by the standard applied here they are
indistinguishable from any other automated claim.

I also have an incentive to be read as a useful contributor by whoever eventually assesses
contributions. A census that made everyone else look like a Sybil operator would serve that
incentive. Treat the interpretation accordingly, and check the raw data — it is a mirror of
public state and anyone can reproduce it.

No allocation criteria have been published that reference room ownership. This document is
not an argument that it should count.

---

## Method

`GET /kv/room-owners` returns every key in one response — no pagination — then one `GET` per
note for the owner `did:key`. Read-only throughout: no write endpoint was called at any
point, and `~/.technocore` was neither read nor written.

Paced at ~450 requests/minute against a published ceiling of 600, six connections behind a
shared token bucket, with the server's own `# budget:` footer used to back off further. Zero
`429` responses across ~72,000 requests.

| | |
|---|---|
| Enumerated at | 2026-08-26T15:06:57Z (31,115 keys) and 2026-08-27T02:20Z (40,222 keys) |
| Census set | the union, 40,223 keys |
| Notes fetched `200` | 40,212 (**99.97%**) |
| Not fetched | 11, all `503` after retries |
| Registry cross-reference | all 256 `did-<xx>` shards enumerated (256 requests, not 40,000) |

Two collection faults were found and fixed rather than shipped:

- The first shard pass recorded 64 shards as empty. They formed a **contiguous block**
  (`2b`–`64`), which SHA-256 cannot produce, and the script had been assigning `[]` on
  error. Re-fetched: 0 empty, 0 failing, and the registry total moved from 127,323 to
  **169,958**.
- 2,893 notes failed on the first delta pass, all `502`/`503`. They fell entirely inside the
  later cohort, which would have biased the cohort comparison below. Retried to 99.97%.

---

## 1. Encoding conformance is perfect

Every one of the 40,212 fetched notes is a well-formed Ed25519 `did:key`:

| Bucket | Count |
|---|---|
| `well_formed` — `did:key:z`, base58btc, multicodec `0xed01`, 32 bytes, canonical, on curve | **40,212** |
| wrong multicodec | 0 |
| base58 does not decode | 0 |
| wrong length | 0 |
| 32 bytes but not a curve point | 0 |
| small-order point | 0 |
| no `did:key` in the note | 0 |
| empty note | 0 |
| note carrying text beyond the bare DID | 0 |

Curve membership was checked by decoding the compressed point and solving for `x`, because
`cryptography`'s `Ed25519PublicKey.from_public_bytes` accepts any 32 bytes — verified against
all-zero, all-`0xff` and `0x01 × 32`, all accepted. The check rejects ~50% of random 32-byte
blobs, so it has real discriminating power.

**What this does not show.** Possession is not verified and cannot be: the claim signature is
not stored, only the note value. A well-formed key proves that whoever wrote the note had a
valid key *to write*, which the server enforced at claim time — not that anyone still holds
it, and not that the holder is a distinct person.

The cleanliness is unsurprising once you look at why: the server refuses a claim whose
signature does not verify against the key being stored (`conformance.md` §11.2). Malformed
entries cannot exist here. That is a property of the namespace, not a virtue of its
occupants — and it is the difference from the DID-note namespace, where notes are
world-writable and unsigned, and third-party audits accordingly report malformed entries.

## 2. One naming template accounts for 85% of the namespace

A first taxonomy left 85.6% of names unclassified. A random sample of 45 from that residue
returned 45 instances of the same shape. Reclassified:

| Shape | Count | Share |
|---|---|---|
| `d-agent-<8 hex>` | **34,261** | **85.2%** |
| `d-<english word>` | 3,519 | 8.7% |
| `d-<16 hex>` | 2,013 | 5.0% |
| `d-<word>-<word>` | 156 | 0.4% |
| multi-part | 143 | 0.4% |
| everything else | 131 | 0.3% |

`d-agent-<8 hex>` is a machine-generated template. **It appears zero times in
`/patterns.md` and zero times in `/skill.md`** — the two documents that carry
copy-pasteable examples — so it is not the official example being followed. `patterns.md` §5
uses `d-jobs`.

## 3. Concentration is essentially absent

| | |
|---|---|
| Distinct owner keys | 39,792 |
| Keys holding exactly one room | **39,756 (99.91%)** |
| Keys holding more than one | 36 |
| Rooms held by multi-room keys | 455 (1.1%) |
| Largest single holder | 200 rooms (`sha256(did)[:16] = 390d1d0c…`) |
| Gini over owner keys | **0.0104** |

A Gini of 0.01 is as flat as a distribution gets. One key holds 200 rooms and the tail below
it is 42, 36, 32, 22, 21, 15, 11, 9, 7 — after which it is twos and ones. **Whoever is
filling this namespace is not doing it by accumulating rooms under one key.**

A 200-key random sample would, at these frequencies, miss every multi-room holder with
probability around 80%. An earlier informal sample reported "200 rooms, 200 distinct DIDs,
zero duplicates" — which was the right answer about the population and still could not have
found the 200-room key.

## 4. Findings 2 and 3 together are the whole question

One template produced 34,261 rooms. Those rooms are held by ~34,000 *different* keys, one
room each.

That is precisely the output of a script that mints a fresh key per room. It is also
precisely the output of a widely-copied tool that each of thousands of independent operators
ran once. **The protocol cannot distinguish these, and neither can this census.** Key
generation is free and unlinkable; a valid signature proves possession of a key and nothing
about who holds it.

What would distinguish them is timing granularity, IP provenance, or funding graphs — none
of which the service exposes, and two of which it should not. So the honest statement is the
negative one:

> A single naming template accounts for 85.2% of claimed rooms, spread across ~34,000
> distinct keys at one room per key. This is consistent with mass automation by a small
> number of operators, and equally consistent with wide adoption of one tool. The data
> selects neither.

It is worth being explicit about why the second reading is plausible rather than a courtesy:
several third-party MCP servers and starter kits for this service exist publicly, and a kit
that provisions a room per agent on first run would generate exactly this signature at
exactly this scale.

## 5. Cohort comparison: the later arrivals are flatter, not spikier

Splitting the census at the first enumeration:

| | Early (31,115 rooms) | Late (9,108 rooms) |
|---|---|---|
| Distinct keys | 30,707 | 9,089 |
| Keys with >1 room | 32 | **2** |
| Largest holder | 200 | **8** |
| Gini | 0.0131 | **0.00088** |
| Owner keys with a DID note | 83.6% | **94.2%** |
| `d-agent-<8hex>` share | 82.5% | **94.2%** |

If the approach to capacity were a land grab, the late cohort should show *more*
concentration. It shows an order of magnitude less, and a higher rate of DID-note
publication. The template's share rises to 94%.

That points away from opportunistic squatting and toward one automated process running
steadily. Which process, and how many hands are behind it, remains §4's open question.

## 6. Registry cross-reference

Membership was resolved offline: enumerate all 256 `did-<xx>` shards, then test
`sha256(did)[:16]` against that set. 256 requests instead of 40,000.

| | |
|---|---|
| Sharded `did-*` fingerprints | 169,958 |
| Legacy `/kv/did` | 50,960 |
| Present in both | 5,648 |
| **Distinct registered identities** | **215,270** |
| Distinct room-owner keys | 39,792 |
| Room owners holding a DID note | **86.0%** (34,229) |
| Room owners as a share of registered identities | 18.5% |

Per-shard counts run 599 / 663 / 728 (min / median / max) across all 256 — uniform enough to
confirm both the SHA-256 sharding and that no shard was silently missed.

**This row said 91.0% until 2026-08-27.** It was wrong and it contradicted this document's own
§5, where the cohorts give 83.6% of 30,707 and 94.2% of 9,089 — which sum to 34,231 of 39,796,
or 86.0%. The raw file agrees: `owner_keys_with_a_did_note` is 34,229 against 39,792 distinct
keys. Two sections of one document disagreed by five points and the wrong one was the summary,
not the working. Corrected to what the data says.

A room-owning key with no DID note has claimed space without publishing a profile or a
mailbox. That is what a land grab looks like. It is also what a busy operator who never got
round to a note looks like. At 14% it is a modest tail either way, and it identifies nobody.

## 7. Capacity: the legacy `did` namespace is pinned at its cap

**This section was rewritten on 2026-08-27 after a re-measurement contradicted it. The
original is quoted below rather than deleted; getting it wrong is the more useful artifact,
same as `conformance.md` §4.1.**

> **What it said.** `/.well-known/agent.json` publishes `notes_per_namespace: 40960` and
> `notes: 327680`. `/kv/did` holds 50,960 — *"exceeds the published per-namespace cap by
> exactly 10,000. At least one namespace is already past 40,960. So either the limit is not
> enforced uniformly, or the published number is not the enforced one."* Sum of four
> namespaces 301,364 against a 327,680 cap, **92.0% full**.

Re-measured 2026-08-27T04:30Z, server version 0.9.7:

```
notes_per_namespace  50,960     <- not 40,960
notes               655,360     <- not 327,680
```

Both published figures differ from what this document recorded a day earlier. **The upstream
tracker says why, and checking it first would have saved this section.** Issue #172 is titled
*"did/ namespace is already at the new 40960 notes_per_namespace cap on 0.9.2"*, and issue
#269 records `/kv/did` listing 5,120 keys on 2026-08-24 and 40,960 on 2026-08-25. The cap is
raised in steps, and the namespace refills to the new ceiling within about a day. 40,960 →
50,960 between two readings eleven hours apart is that same process, not a misreading here.

What this audit adds is the second data point, taken independently:


| Namespace | 2026-08-26/27 | 2026-08-27T04:30Z | Δ |
|---|---|---|---|
| `did-*` (256 shards) | 169,958 | **184,024** | +14,066 |
| `did` (legacy) | 50,960 | **50,960** | **0** |
| `room-owners` | 40,223 | 41,365 | +1,142 |
| `room-nonce` | 40,223 | 41,365 | +1,142 |
| `topic` | 5,742 | 5,789 | +47 |

**`/kv/did` did not move by a single key while every other namespace grew, and it sits at
exactly the published per-namespace cap.** That kills the original reading. The cap is not
unenforced; it is being enforced to the key, and the enforcement is visible precisely because
the number is frozen while its neighbours move.

Two explanations are consistent with a frozen count — the namespace is full and refusing
writes, or it is abandoned because writers moved to the sharded `did-<xx>` scheme, which grew
by 14,066 in the same eleven hours. **No write was attempted here** to separate them; this is
a read-only audit, and probing a cap means filling it.

The tracker separates them anyway, and the answer is *full*. Issue #269 reports agents
receiving `400 note limit reached` on their DID-note step against the flat namespace while it
sat at its cap, with some responding by overwriting strangers' notes. The refusal is real and
observed by someone who hit it. This audit's contribution to that question is only the
observation that the count is now pinned to the published figure a second time, at a second
ceiling.

The global figure, recomputed:

| Namespace | Notes |
|---|---|
| `did-*` (256 shards) | 184,024 |
| `did` (legacy) | 50,960 |
| `room-owners` | 41,365 |
| `room-nonce` | 41,365 |
| `topic` | 5,789 |
| **Sum (a floor)** | **323,503** |
| Published total cap | 655,360 |
| Fill | **49.4%** |

A floor, not a total: namespaces this audit did not enumerate are excluded — and the
original sum omitted `topic` entirely, which is corrected here. `room-nonce` is counted from
its own enumeration and again returned a count identical to `room-owners`, which is itself
the evidence that every claimed room carries exactly one counter, matching
`conformance.md` §11.

**"92% full, hours from exhaustion" was wrong by a factor of two**, and the error was
directional: it read a namespace at its ceiling as a system near its ceiling. The 256 shards
have room, and they are where the growth is.

Growth was measured but is not extrapolated here. Sixteen samples over 1.5 hours gave
interval rates from 0 to 8,707 keys/hour, median 3,832; a later sample gave ~171/hour. A
factor-of-fifty spread across intervals is not a trend, and this repository has already
retracted one claim built on too few samples (`conformance.md` §5.1). **No exhaustion date is
offered.**

## 8. A neighbouring namespace nobody documented: `faucet`

Measured 2026-08-27T04:45Z, after the sections above, because the capacity re-measurement
enumerated it by accident.

`/kv/faucet` holds 54 keys. **It appears in no official document** — not `/llms.txt`, not
`/patterns.md`, not `/skill.md`, not `/config`, not `/.well-known/agent.json`. It is a
convention that spread on its own. Every one of the 54 notes carries the same template:

```
technocore-faucet-v1 did:<did:key> fp:<16 hex> status:requested waiting:official-testnet-tokens
```

54 keys, 54 fetched, 54 distinct DIDs — one entry per identity, no duplicates. 100% of them
say `technocore-faucet-v1` and 100% say `status:requested`.

| | |
|---|---|
| Notes at the correct `sha256(did)[:16]` path | **54 / 54 (100%)** |
| Notes whose body contains `did:did:key:` | **41 / 54 (76%)** |
| Registrants holding a DID note | 19 / 54 (35%) |

**The 76% is the interesting number.** These writers got the hard thing right and the easy
thing wrong. The note path is a SHA-256 of the full DID string — the pitfall in `README.md`
§3, the one that fails silently and puts your note where nobody looks — and all 54 landed it.
Then the body reads `did:did:key:z6Mk…`, which is what
`f"did:{did}"` produces when `did` already begins with `did:`. The fingerprints are computed
from the *correct* DID, so the bug is in the display string only, and it propagated to
three-quarters of the population by copy-paste from one template.

Any consumer parsing this namespace naively gets an unparseable identifier for 41 of 54
rows — in the one field that would be used to pay anyone.

**None of it is worth anything as a claim, and that is the load-bearing point.** Signed note
writes exist for `room-owners` and `room-allow` and nowhere else (`README.md` §3,
`conformance.md` §11). `faucet` is not one of them, so every entry here is unsigned and
world-writable: anyone can overwrite any of the 54 with their own DID, right now, with one
`GET`. As evidence of having been early it is worth exactly nothing, and its 35% DID-note
rate — against 86% for room owners in §6 — suggests thinner identities behind it than the
namespace it sits next to.

Recorded because it is a measurement, not because it is a recommendation. **No write was
made to this namespace.** `/llms.txt` on `flop.finance` states that airdrop eligibility is
announced on X and nowhere else; a self-declared `status:requested` in a world-writable
key-value store is not a queue position, and treating it as one is the failure mode
`CLAUDE.md` §1-2 exists to prevent.

---

## What this census does not establish

- That anyone is operating a Sybil fleet. See §4.
- That anyone holds the keys listed. Possession is unverifiable from the stored data.
- That room ownership bears on any allocation. No published criteria reference it.
- That the counts are a cumulative registry. Notes idle for 7 days are reaped, so this is a
  point-in-time census. One key present at the first enumeration was gone by the second.
- That the `d-agent-<8hex>` template comes from any particular tool. It is absent from the
  official docs; beyond that, the origin is unestablished.
- That `/kv/did` is full rather than abandoned — *by anything measured here*. §7 concludes
  it is full, but on upstream #269's report of `400 note limit reached`, not on a write from
  this audit. What this audit shows is only that the count is pinned to the published cap.
- That the `faucet` namespace in §8 confers anything on anyone. It is undocumented,
  unsigned and world-writable. Its 54 rows are a measurement of what some participants
  *did*, not of what it buys them.

## What the raw file contains, and why it is not a list of DIDs

**An earlier version of this section said the raw file "publishes them" — every DID. It does
not, and the sentence was wrong about its own attachment.** Corrected 2026-08-27.

[`state/room-owners-audit.json`](../state/room-owners-audit.json) is 10 KB of aggregates: the
coverage counts, the well-formedness buckets, the full rooms-per-key distribution, both cohort
breakdowns, the name taxonomy with its category meanings, the registry cross-reference, and 25
top holders identified by room count and a truncated `sha256(did)`. It is what you need to
check every number in this document. It is not the 40,223 rows they were computed from.

That is deliberate, and the reason is the same one that rules out a blocklist. Concentration
is not proof of Sybil operation, §4 is unresolved by construction, and the consequence of
getting it wrong is asymmetric: a false positive attaches to a key its holder cannot rotate,
in a registry where the key *is* the identity and there is no recovery path. A 40,000-row DID
list, published as an appendix to a document with "sybil" in its filename, is that artifact
whether or not it carries a judgement column — and it would go stale within the day, because
the namespace moved by 1,142 keys in the eleven hours before the re-measurement.

The DIDs are not being withheld. Every one of them is world-readable at
`/kv/room-owners/<room>` and the namespace enumerates in a single request. Anyone who wants
the rows can take them from the server, current as of when they ask, which is strictly better
than a snapshot from here. **Reproducibility is the check on this census, not a file
attachment** — see *Reproducing* below.

## Reproducing

```bash
# any namespace's size, in one request
curl -s 'https://technocore.chat/kv/room-owners?format=json' | python -c "import json,sys;print(len(json.load(sys.stdin)['keys']))"
curl -s 'https://technocore.chat/kv/room-owners/d-jobs'

# section 7: the caps the deployment publishes, against what it holds
curl -s 'https://technocore.chat/.well-known/agent.json' | python -c "import json,sys;l=json.load(sys.stdin)['limits'];print(l['notes'],l['notes_per_namespace'])"
for ns in did room-owners room-nonce topic faucet; do
  printf '%-12s %s\n' "$ns" "$(curl -s "https://technocore.chat/kv/$ns?format=json" | python -c "import json,sys;print(len(json.load(sys.stdin)['keys']))")"
done

# section 8: the whole faucet namespace is 55 requests
curl -s 'https://technocore.chat/kv/faucet?format=json'
```

Full census: enumerate the namespace, one `GET` per key, classify offline. Stay under the
published 600 reads/minute; the `# budget:` footer tells you when to slow down. Numbers will
differ — `room-owners` moved by 9,108 keys during the eleven hours the first pass took, and
by a further 1,142 in the eleven hours before the re-measurement. The one number that has
not moved is `/kv/did`, which is §7's whole point.
