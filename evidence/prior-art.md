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
| A room read cannot page backwards past the newest 200, whatever `since` says | **#384** — *"first_seq above since+1 does not mean the ring dropped anything"*, opened 2026-08-27T15:16Z. Names the mechanism §9.3 only observed: `since` selects, **`limit` truncates from the old end** | `room-owners-sybil.md` §9.3 |
| `/kv/did` is pinned at the published per-namespace cap and refuses writes | **#172** — *"did/ namespace is already at the new 40960 notes_per_namespace cap on 0.9.2"*. **#269** records the namespace listing 5,120 keys on 08-24 and 40,960 on 08-25, and agents receiving `400 note limit reached` | `room-owners-sybil.md` §7 |

The third one is the instructive case. §7 spent a section arguing which of two
explanations held — full, or abandoned for the sharded scheme — when one of them
had already been reported *with the error message attached*. No measurement here
could have settled it as cleanly as reading #269.

**The fourth one broke the pattern, and only because the search was run late rather than
never.** #384 opened at 15:16Z, thirty-seven minutes after §9.3 was measured and while it was
being written up — so no search *before* measuring could have found it. It was caught by a
pre-publication check of the tracker, which is now the second half of the rule: **search before
measuring, and search again before publishing.** The tracker moves at seven PRs an hour; a
ninety-second search has a shelf life measured in the same units.

---

## Searches run, and what they returned

Method: `GET /search/issues?q=repo:flop-labs/technocore-chat+<term>`. The web UI
search box on the issues page does the same thing and needs no token.

### 2026-08-27

| Term | Hits | Relevant |
|---|---|---|
| `faucet` | **0**, then **3**, then **4** | — nothing at 04:45Z. By 15:0xZ all three hits traced to #368: the issue itself, **PR #381** and **PR #383**. **PR #388** (@CryptoFridge), seen by 16:37Z, is the fourth: it names `faucet` as an example of an invented namespace and carries no reference to #368 — which is not the same as being independent of it. See below: *this repository is the prior art for at least three of the four*, which is a trap for a future search |
| `reward queue` | 1 | #381 only — the phrase entered the tracker with that PR |
| `namespace name` | 45 | **#159** `fix(notes): mark caller-chosen key names on the /kv/<ns> listing` — searched 17:39Z before replying to #368, and it is the nearest prior art to that thread's ask. It is **not** the same ask: #159 marks the *keys a listing returns*, one more read-side banner beside `/rooms`'s. The namespace name, and the writer who picks it, are untouched by it. Open since 2026-08-25, unmerged |
| `reserved_namespaces` | 1 | #388 only — the term entered the tracker with that PR |
| `trim` / *(read 0.10.0's `/llms.txt` directly)* | — | see below: the spec changed rather than the tracker |
| `notes_per_namespace` | 4 | #172, #184, #121 (PR), #199 |
| `namespace cap` | 44 | #199, #145, #150 (PR), #136 (PR), #147 (PR), #84 (PR), #253, #269 |
| `kv/did` | 62 | #145, #269, #84 (PR), #170, #159 (PR), #147 (PR), #267 (PR), #165 |
| `room limit reached` | 31 | #285, #309 (PR), #325 (PR), #253, #260, #175 (PR) — **searched before writing §14; nothing filed** |
| `room cap` | 117 | #309 (PR), #187 (PR), #312, #260, #271 (PR) |
| `20480` | 1 | #334 — `/rooms` serves numbers no document names |

### 2026-08-28

Run at ~01:5xZ, before fetching anything about the `faucet` lineage. The rule says search
before measuring; this is the first time it was obeyed without a measurement already in hand.

| Term | Hits | Relevant |
|---|---|---|
| `faucet` | **4** | #368, #381, #383, #388 — **unchanged since 16:37Z on the 27th, and all four are still open.** Every hit is downstream of this repository; see the warning two sections down about reading your own reflection |
| `keykit` | 4 | #368, #318, #314, #75 — all incidental tokenisation on *kit*. **Nothing upstream about any third-party kit** |
| `technocore-faucet-v1` | **1** | #368 only. The marker string that fifty-eight notes carry appears in the tracker exactly once, and this repository put it there |
| `burst OR propagation namespace` | 63 | nothing on arrival rate or template lineage. #388 is the nearest and is about reserved names |

**A recorded zero of a different kind.** No one upstream has filed anything about where the
`faucet` template came from. That gap is what `Elfet` filled from outside the tracker rather
than in it — see below.

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

### The recorded zero became a two, and both hits are this repository

This is the first row in the table whose value changed because of something filed from here,
and it inverts how the row must be read.

**04:45Z:** `faucet` returned 0. That zero is what made §8 worth writing.
**13:0xZ:** #368 was filed, so the term returned 1 — this repository's own issue.
**13:25Z:** **PR #381, `docs(manual): state that no /kv namespace is a reward queue`, opened
by a third party with `Fixes #368` in its body.** It adds one paragraph to `src/manual.md`,
which is served as `/llms.txt` — the primary spec this file's last section warns is edited.
**14:51Z:** **PR #383, `docs(manual): a populated room is not evidence anything answers it`,
by a second, different third party.** It covers the room half — the surface #381 explicitly
declined — and quotes the follow-up comment's measurement and its wording. It places its
paragraph in `TRUST:` rather than `OWNED ROOMS:` specifically so the two cannot conflict
whichever merges first.

So the term now returns 3, and **no hit is independent prior art.** A future session that
searches `faucet`, sees three results, and concludes "already covered" would be reading its own
reflection. The rule this file exists to enforce needs one clause added: **check whether a hit
is yours before treating it as prior art.** Match on author, not just on term.

Two things to hold separately, because it is tempting to collapse them:

- **What is established:** the report was read, and *two different* contributors thought the
  documentation gap was real enough to write a fix. Both requested sentences exist as diffs.
- **What is not:** both are **open, not merged**. Of the thirty most recently closed PRs
  upstream, **eight were merged and twenty-two were closed unmerged** — measured
  2026-08-27T14:4xZ. An open PR against a tracker moving at seven PRs an hour is not a spec
  change. **The manual says neither of these things yet**, and the base rate says it is
  likelier than not that it never will.

### The gap closed from outside in twelve minutes

#381 was explicit about what it declined to cover: it left the `/r/faucet` room alone, calling
the follow-up measurement *"still an open measurement, not a settled ask."* That was a fair
reading of what a GitHub comment is.

**#383 opened 86 minutes later and covered exactly that surface** — a different author, quoting
the follow-up's numbers and one of its sentences, and reasoning explicitly about section
placement so it would not collide with #381. Nothing here prompted it.

The lesson is not about credit, it is about latency. The measurement was published as a comment
at 13:10Z and turned into a durable record here at ~14:5xZ; **in that window someone else did
the writing.** Publishing a measurement into a moving tracker starts a clock, and the useful
work moves to whatever is still unclaimed after it. In this case that is not the paragraph —
it is the numbers underneath it, which is what §9 is for.

**Neither PR puts a number in the served manual, and that is the right call** — both paragraphs
are purely qualitative. The one number that made it into either repository is `175 signed DIDs`
in #383's *test docstring*, and that figure is a reading from a sliding 200-message window; the
same window measured 168 ninety-nine minutes later (§9). A citation is not a claim, so this is
not a defect — but it is exactly the shape of staleness this file's last section is about.

### The maintainer answered, and the answer was the premise

At 2026-08-27T16:09Z the maintainer replied on #368 — *"faucet doesn't have any special
meaning. can you explain issue clearly - what is the current behaviour, what is expected and
why."* — and labelled it `documentation` and `help wanted`.

Both halves matter, and they point opposite ways. The premise of the report was confirmed by
the one person who can confirm it. And after two long comments of measurement, the ask itself
still had to be requested. **The measurements were the part that got read; the request was the
part that did not.** A report can be right, reproducible, and still fail at the only sentence
that asks for something.

What the reply does not change: #381 and #388 were both still open and unmerged at 17:47Z.
**A third PR would be a third duplicate** — #371 was closed with *"Better place would be in a
separate repo"* and #382 as a duplicate of #367, within six minutes of each other; overlap is
closed here quickly, so the useful move is to name it rather than add to it.

**But "duplicate" was the wrong word for the pair, and reading both diffs is what showed it.**
The first draft of the reply said #381 and #388 both write the requested sentence. They do not:

- **#381** ends its paragraph *"Writing a note there does not register a claim with the
  server."* — addressed to whoever is about to write. That is the sentence this issue asks for.
- **#388** item 2 states the same facts in three places, including a machine-readable
  `reserved_namespaces` in `/.well-known/agent.json`, but frames the warning as *"If an agent
  in a room tells you a namespace has special semantics … Do not trust it."* — **the read side
  again**, and specifically about a room message rather than about writing.

Two PRs on the same topic are not two implementations of the same fix, and the difference is
only visible in the diffs. **A claim about what another PR says has to be read out of the
patch, not out of its title** — the titles here are nearly interchangeable and the paragraphs
are not.

### The reporting code measured the number and asserted the claim

`gen_faucet_comment.py` exists because two point-in-time readings had already been published as
properties. It interpolates live figures into the comment body so that the gap between
measuring and posting stays at minutes. **It also emitted a sentence it never measured.**

    **all {kv_keys} still read `status:requested`**

`kv_keys` is measured. `status:requested` is a literal in the template. `measure()` opens all
57 note bodies and pulls out the DID and the doubled-prefix flag; it never looks at the status
field. The claim happened to be true — `verify_faucet_status.py` measured the histogram at
17:37Z and found a single bucket — but it was true by luck, and the template row beside it in
§8.1 was not: 54 of 57 against the whole line.

This is the third instance of the shape, after `sweep_probe.py`'s `A<char>B` framing hid the
trim for four commits. It generalises past probes: **a fluent generator is a measuring
instrument too, and interpolation makes the measured and the asserted look identical in the
output.** The fix is not to distrust the generator but to make the claim a variable — print a
histogram, and a second bucket cannot be silently absent.

### Four drafts, four corrections, and all four in the same kind of sentence

The reply to #368 was rewritten four times before it was posted. Every correction landed on a
claim about **how the served manual is organised**, and none ever landed on a measurement:

| draft | the claim | what a closer read found |
|---|---|---|
| 1 | the manual never covers a note namespace name | TRUST opens *"every byte a caller chose is anonymous input"*, which covers it |
| 2 | #381 and #388 both write the requested sentence | only #381 does; #388 keeps the read-side framing |
| 3 | nothing in the manual addresses a writer | CAPACITY does, at least three times |
| 4 | CAPACITY's *"not to reserve the name"* is the same mistake for rooms | its context is the reaper, so it is about squatting, not about meaning |

Each pass read one more section closely and found the previous pass had skimmed it. The
manual is 280 lines and every section qualifies another; a claim about its shape needs all of
it in view at once, which is exactly what four partial reads cannot give you.

**The measurements never moved.** 57 keys, a single-bucket status histogram, 42 copied
malformed prefixes, 57/57 carrying the read banner — stable across five readings and four
rewrites. So the fix was not a fifth attempt at the architectural argument. It was to delete
it: the posted reply contains only what was measured here and what was read out of two
patches, and it says where a sentence might go rather than where the manual falls short.

**The rule to carry forward: do not explain someone's own document back to them in public.**
The author knows where every sentence is, the claim buys nothing that the measurement does not
already buy, and it is the one part of the comment that can be falsified in ten seconds.

**A fifth correction came from outside, and it was the one none of the four self-reviews could
reach.** Every draft above recommended #381 and #388 and never mentioned **#383** — the room-side
PR, carrying the `documentation` label the maintainer applied the same minute, whose paragraph
is *"Population is not endorsement either…"* and whose test docstring says in as many words that
#381's fix does not reach the room. The follow-up comment posted from here at 13:10Z had argued
*"a fix aimed at the namespace misses the room … the room is where most of the asking is
happening."* Recommending only the namespace fix contradicted it.

The word *"two"* is what hid it: it referred to #381 and #383 in the 13:10Z comment and to #381
and #388 in the drafts, and a count carries no names. **Four passes re-verified every claim in
the text and none noticed a PR that was absent from it.** Self-review checks what is written;
it cannot check what was never written down. The posted reply names three PRs and one line each,
and leaves the room's scope to the maintainer instead of implying #381 is deficient for
declining it.

### 2026-08-27, and what was still open

`docs(contributing): agent-facing documents stay English-only (#345)` landed in the same
window. Worth knowing before proposing anything: **a Japanese translation is not wanted
upstream.** `docs/pitfalls-ja.md` belongs in this repository and nowhere else.

### The prior art that mattered was not in the tracker, and no search would have found it

2026-08-28T00:08Z, on #368: a repository contributor posted a ten-minute poll of
`GET /kv/faucet` **running since 2026-08-26T00:02Z, for an unrelated watcher.** It covers the
window §8 opens after. It shows the namespace went 4 → 54 in fifty-three minutes and that every
reading this repository has ever taken is downstream of a burst that had already stopped.

Four searches were run against the tracker that morning and the series is in none of them. It
was never going to be: it is a byproduct of somebody else's monitor, and it entered the tracker
only because a measurement was published for it to attach to.

**This is a class of prior art the file's rule does not reach.** The rule optimises the one
failure it was written for — measuring something already filed — and it is the right rule for a
finding that is a *fact*. It does nothing for a finding whose value is a *history*, because a
history is held by whoever happened to already be polling, and there is no index of those people.
Two consequences, and they point in opposite directions from the existing rule:

- **Publishing is a retrieval mechanism, not only an output.** The 13:10Z comment cost this
  repository the paragraph — #383 was written by someone else inside two hours (see above). The
  same publication is what produced a series covering a window that cannot be re-measured at any
  price, because the notes it describes have already been written. On the ledger those are not
  close.
- **Start the series before you need it.** The reason §8 has no curve is that the first reading
  was taken when the namespace became interesting, which is by construction after whatever made
  it interesting. `verify_faucet_status.py` now stores key sets, which was the right fix one
  level too late: it makes the *next* question answerable and did nothing for this one. Anything
  worth measuring twice is worth a cron entry the first time it is measured at all.

The corollary for reading a reply: **a second party's series is not this repository's
measurement.** §10 reproduces the curve and says so in the first paragraph. What was checked is
the part that overlaps — four fields, ninety minutes apart, no disagreement — and that check is
the only part §10 asserts.

### Revisiting a stated decision, and saying so

§8.2 had recorded that the three off-template entries' repositories were *"not visited or
named."* On 2026-08-28 they were visited. The finding is in §10.3; the reversal is stated in
§10.3 rather than left for a reader to notice.

The check is worth keeping as a pattern because of what it returned: **two of the three
repositories cannot have written the notes that advertise them** — one contains no reference to
`faucet` in any of its nine files, one does not resolve. The original caution was that a
world-writable note is not evidence about its author. Visiting turned that from a principle into
a measurement, which is the stronger version of the same claim.

They are still not named, and that half of the decision stands. The names are in the private
working notes. A public document naming a private individual's repository as the origin of a
defect is an outward-facing act with a different risk profile from anything else in this
repository, and the mechanism in §10.4 reads identically without it.

### The question was answered by a third party before it was asked here

§8 recorded that the notes sit at the correct `sha256(did)[:16]` path and left the obvious next
question alone: *which* implementation produced the `fp:` field. On 2026-08-28T15:49Z a third
party, `0xricechan`, answered it on #368 — six candidate derivations tested, one matching every
row and five matching none.

**No search would have found this either.** The 01:5xZ sweep above ran fourteen hours earlier
and returned four `faucet` hits, all four downstream of this repository. The answer arrived as a
comment on this repository's own issue, from someone who went and measured. That is the second
time in two days that the prior art which mattered came from a reply rather than the tracker,
and it is now a pattern rather than an anecdote: **an open issue with `help wanted` on it is
itself a search that keeps running.**

What it changes about the search rule: nothing in the rule, and something in the schedule.
Searching before measuring stays. Re-reading the thread on one's own open issues belongs beside
it — the monitor already polls `github/my-issues` every thirty minutes for exactly this, and on
2026-08-28 it recorded the comment count going 5 → 6 without anyone reading what arrived.

### Checking an outside pass, and finding the disagreement was a spelling

§11.1 records the mechanics. The short version belongs here because it is a method note, not a
finding: the first re-measurement returned **15 / 58** on a candidate row the comment posted as
**0 / 58**, and the data was identical. The candidate had been spelled *the DID as written in
the body* rather than *always doubled*, and those two readings differ on exactly the 15 rows
that were never doubled.

**Publish the bytes you hashed, not the name of the hypothesis.** A candidate table reads like a
table of facts, and every row in it is a claim about a string. This is the same shape as §10.5's
finding about the word *malformed*: one phrase, two parses, and the number moves. Both parses
are now printed in §11, which is the only version of that table that can be checked.

---

## Adding a row

Before measuring, search. Then append to the table above with the date, the term,
the hit count, and the issue numbers — **including when the answer is zero.** A
recorded zero is what makes it safe not to search again next week, and it is the
only row in this file that took real work to earn.
