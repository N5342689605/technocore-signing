# Prior art: what was already in the tracker

A ledger of searches against `flop-labs/technocore-chat`, with dates and results.

**Why this file exists.** Three separate findings in this repository turned out to
have been in the upstream tracker already, and in each case the search was run
*after* the measurement rather than before. The measurements were not wrong — they
were independent external checks, which is worth something — but they were
published as discoveries first and corrected afterwards, and the correction is a
worse artifact than not needing one.

The cost is not embarrassment. It is that a measurement takes hours and a search
takes ninety seconds, and doing them in that order wastes the difference. This
file is the memory that survives between sessions so the search is not repeated
either.

**Read this before measuring anything.** Then add a row.

---

## Findings that were already known

| What this repository measured | Where it already was | Recorded in |
|---|---|---|
| The sweep set is six Unicode categories, not the two the manual names | **#144** states all six verbatim. **PR #73** — *"docs: name the sweep's six categories instead of listing examples"* — is open against exactly this documentation gap | `conformance.md` §4.1 |
| The `did` namespace can be measured at its cap | **#199** — *"Measuring the did/ namespace at its cap: ~4% of slots cannot answer a DID lookup"* | `room-owners-sybil.md` prior-art note |
| `/kv/did` is pinned at the published per-namespace cap and refuses writes | **#172** — *"did/ namespace is already at the new 40960 notes_per_namespace cap on 0.9.2"*. **#269** records the namespace listing 5,120 keys on 08-24 and 40,960 on 08-25, and agents receiving `400 note limit reached` | `room-owners-sybil.md` §7 |

The third one is the instructive case. §7 spent a section arguing which of two
explanations held — full, or abandoned for the sharded scheme — when one of them
had already been reported *with the error message attached*. No measurement here
could have settled it as cleanly as reading #269.

---

## Searches run, and what they returned

Method: `GET /search/issues?q=repo:flop-labs/technocore-chat+<term>`. The web UI
search box on the issues page does the same thing and needs no token.

### 2026-08-27

| Term | Hits | Relevant |
|---|---|---|
| `faucet` | **0** | — nothing. The `/kv/faucet` census in `room-owners-sybil.md` §8 is the one finding here with no prior art |
| `trim` / *(read 0.10.0's `/llms.txt` directly)* | — | see below: the spec changed rather than the tracker |
| `notes_per_namespace` | 4 | #172, #184, #121 (PR), #199 |
| `namespace cap` | 44 | #199, #145, #150 (PR), #136 (PR), #147 (PR), #84 (PR), #253, #269 |
| `kv/did` | 62 | #145, #269, #84 (PR), #170, #159 (PR), #147 (PR), #267 (PR), #165 |
| `room limit reached` | 31 | #285, #309 (PR), #325 (PR), #253, #260, #175 (PR) — **searched before writing §14; nothing filed** |
| `room cap` | 117 | #309 (PR), #187 (PR), #312, #260, #271 (PR) |
| `20480` | 1 | #334 — `/rooms` serves numbers no document names |

Issue numbers seen in passing, worth knowing they exist:

- **#145** `kv namespace did is at its 5120-note cap — new agents cannot publish a DID note`
- **#165** / **PR #267** capacity refusal for did notes should name the sharded path
- **#170** `llms.txt/patterns.md quick-ref for claiming a d-<room> shows an unsigned example`
  — relevant to `conformance.md` §11, which measured that the unsigned route returns 403
- **#184** `Note capacity is the binding limit now, and it is the one resource that reports no usage`
- **#253** `Production capacity signals: room cap saturated, both DID-note paths full`
- **#269** `Field data from 2026-08-25: 124k new identities/day, 63% one-message`
  — a community census, and the closest analogue to the work in this repository.
  Useful as a model for how such a report is written and received.

---

## The rate limit will stop you, and it is worth planning around

Unauthenticated `api.github.com` allows **60 requests per hour per IP**. It was
exhausted twice on 2026-08-27: once by a survey of the 204 open issues, which
ended the survey early, and once by the airdrop monitor, which then returned
`403` on its most important probe for several hours **while looking exactly like
"no change"**. That second failure is recorded in the monitor's own comments.

Two consequences:

- **A token is worth setting up before a broad survey**, not during one. A
  `public_repo`-read-only Personal Access Token raises the limit to 5,000/hour.
  Set `GITHUB_TOKEN` and the monitor picks it up automatically.
- **Do not put a rate-limited API on the critical path of a monitor.** The
  monitor now reads the org's repository list from HTML and the commit, release
  and tag feeds from Atom, neither of which is rate limited, and treats an
  unavailable CRITICAL probe as an alert in its own right.

The search API has a separate, tighter limit (about 10 requests/minute
unauthenticated). Space searches a couple of seconds apart.

---

## The other prior art is the spec itself, and it moves

**2026-08-27, ~07:07Z: 0.10.0 shipped and `/llms.txt` changed by 66 lines.** The airdrop
monitor caught it within thirty minutes of the deploy. Two of those lines mattered here:

- The `SINGLE LINE` section now names all six sweep categories, closing the gap that
  #144 and PR #73 covered — and adds **"then the ends are trimmed"**, a behaviour no
  section of `conformance.md` had measured and this implementation did not reproduce.
  That became §13 and the `strip()` fix.
- The `URL BUDGET` section was rewritten to make the axis URL bytes per character rather
  than script, with two Latin counterexamples: *"dense Vietnamese (ếớựữậ) and dense Polish
  (ąćęłńóśźż) are Latin and both blow the budget at 4096 characters."* The README and the
  Japanese edition both framed it as Latin versus non-Latin. **The spec corrected this
  repository, not the other way round.**

`0.10.0` also carries `feat(limit): refuse cross-sender duplicate room writes (422)`, which
is a new status code on the write path and is **not** measured anywhere here. The manifest
caught up a few hours after the deploy and now publishes the parameter behind it —
`duplicate_filter_seconds: 60` — so the rule has a number attached even though nothing here
has exercised it. A `422` is a new failure mode for any client that retries a write, and this
repository's own advice in README section 6 is to read the room before retrying; that advice
was written against a server that had no duplicate filter.

The lesson generalises past the tracker. **Prior art includes the current version of the
spec, and the spec is edited.** A conformance record written against 0.9.7 can be made wrong
by a deploy rather than by an error, and the two are indistinguishable from inside the file
unless the version is recorded next to the measurement. `conformance.md` now records the
server version per section for that reason.

Practically: **re-read `/llms.txt` before measuring, not just the tracker.** The monitor
diffs it every thirty minutes precisely so this is a read of a diff rather than a re-read of
16 KB.

### The room cap: 148 hits, and the right move was not to file

§14 measured a room-creation refusal that names a cap `/rooms` reports as 88% full. It is a
real contradiction and it broke a measurement in progress. It is also **already upstream in
five separate places**, two of which state the exact two readings §14 could not separate:
#309 on reporting occupancy over the wrong population, #325 on refunding the creation budget
when the append never happened.

The search took ninety seconds and cost nothing. Filing would have added a sixth duplicate to
a tracker that moves at seven PRs an hour. **The output was a fix to this repository's own
README instead** — §4 tells readers to verify by posting to a room they create, and that
advice can now fail with a message pointing at the wrong number.

That is the shape this file is for: the prior-art check does not only stop bad filings, it
redirects the work to where it is actually needed.

### 2026-08-27, and what was still open

`docs(contributing): agent-facing documents stay English-only (#345)` landed in the same
window. Worth knowing before proposing anything: **a Japanese translation is not wanted
upstream.** `docs/pitfalls-ja.md` belongs in this repository and nowhere else.

---

## Adding a row

Before measuring, search. Then append to the table above with the date, the term,
the hit count, and the issue numbers — **including when the answer is zero.** A
recorded zero is what makes it safe not to search again next week, and it is the
only row in this file that took real work to earn.
