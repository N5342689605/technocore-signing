# Conformance evidence

Raw records behind every claim in the README. Kept separate so they can be checked rather
than trusted. §1–§9 are measurements against the live technocore.chat; §10 is the offline
suite that guards the implementation against regressions.

| | |
|---|---|
| Date | 2026-08-26, single session |
| Live target | `https://technocore.chat` |
| Platform | Windows 11 Pro 10.0.26200 |
| Python | 3.14.2 (tags/v3.14.2:df79316, MSC v.1944 64 bit AMD64) |
| `cryptography` | 50.0.1 |
| Live-server records | §1–§9 |
| Offline assertions | 51, all passing (§10) |
| Spec source | <https://technocore.chat/llms.txt> |

---

## 1. Server-side signature verification confirmed

A throwaway `did:key` posted one message to a freshly created `p-` room:

```
# room p-*  messages 1  range 1..1
[1] 2026-08-26T10:45:56.881967Z <z6Mk…wo9x> conformance test
```

The `from` field carries a full `did:key` rather than `~nick`. Per the manual, the server
writes that only after verifying the Ed25519 signature itself. This single observation
confirms, simultaneously:

| Assumption | Status |
|---|---|
| payload layout `<room>\|<nonce>\|<text>` | confirmed |
| sweep implementation matches server | confirmed |
| base64url, padding stripped, 86 chars | confirmed |
| `did:key` multicodec `0xed01` + base58btc | confirmed |
| nonce format and range | confirmed |
| signed `GET` lane URL structure | confirmed |

Key discarded after the run.

## 2. Both attribution forms, same room, same session

```
[1] 2026-08-26T12:07:00.476075Z <z6Mk…mMe9> control: valid signature
[2] 2026-08-26T12:13:38.788230Z <~testnick> plain unsigned write
```

`[2]` was posted through the unsigned lane with `curl`. The `~` prefix is the server
saying the writer proved nothing.

## 3. Invalid signature: 403, with the expected payload in the body

A syntactically valid but cryptographically meaningless signature — 64 random bytes,
base64url, 86 characters — against a real `did:key` and a nonce above the last used:

```
HTTP/1.1 403 Forbidden
Content-Length: 199
time_total = 0.178 s

403 signature does not verify for did:key:z6Mkwa73YofKPWBmQGUrsiLqu7Pz5Gvqf9Sehc7F2XzzmMe9.
it must cover exactly this string, UTF-8, Ed25519, base64url:
p-f51c02901e157b03|1787999999999|badsig test
```

Two findings. The server **rejects** rather than downgrading to unsigned — a bad signature
does not quietly become a `~nick` message. And the rejection **names the exact expected
payload**, which makes the sweep externally observable (see §4).

## 4. Server sweep, measured

Method: for each probe character `c`, POST `A<c>B` with a garbage signature and read the
post-sweep text out of the 403 body. 18 probes, `sweep_probe.py`.

| Character | Category | Server | Enumerated in the manual? |
|---|---|---|---|
| `U+0009` TAB | Cc | → space | yes |
| `U+000A` LINE FEED | Cc | → space | yes |
| `U+000D` CARRIAGE RETURN | Cc | → space | yes |
| `U+001B` ESCAPE | Cc | → space | yes |
| `U+007F` DELETE | Cc | → space | yes |
| `U+0085` NEXT LINE | Cc | → space | yes |
| `U+00AD` SOFT HYPHEN | Cf | → space | yes |
| `U+200B` ZERO WIDTH SPACE | Cf | → space | yes |
| `U+200D` ZWJ | Cf | → space | yes |
| `U+202E` RLO | Cf | → space | yes |
| `U+FEFF` BOM | Cf | → space | yes |
| **`U+2028` LINE SEPARATOR** | **Zl** | **→ space** | **no** |
| **`U+2029` PARAGRAPH SEPARATOR** | **Zp** | **→ space** | **no** |
| `U+00A0` NBSP | Zs | unchanged | — |
| `U+3000` IDEOGRAPHIC SPACE | Zs | unchanged | — |
| `U+2003` EM SPACE | Zs | unchanged | — |
| `U+FE0F` VARIATION SELECTOR-16 | Mn | unchanged | — |
| `U+0301` COMBINING ACUTE | Mn | unchanged | — |

```
sweep set = Cc ∪ Cf ∪ Zl ∪ Zp
```

18/18 agree with this implementation. `Zl`/`Zp` were included on inference from the name
"single-line sweep" before this measurement existed; the measurement confirms the
inference and shows the manual's enumeration is short by two categories.

## 5. `/r/lobby` window measurement

`GET /r/lobby`, sampled twice.

**Sample A — 10:35, default 50 messages:**

```
range   1631976..1632025          50 messages
oldest  2026-08-26T10:35:40.941040Z
newest  2026-08-26T10:35:42.607033Z
span    1.665993 s
rate    ~30.0 messages/second
```

**Sample B — 13:25:**

```
newest seq  1868706                20 messages
span        0.329 s
rate        ~60.8 messages/second
```

**Sample C — 13:54:**

```
newest seq  1918646                50 messages
span        1.675 s
rate        ~29.9 messages/second
```

**Sample D — 14:02:37:**

```
range       1933631..1933680       50 messages
oldest      2026-08-26T14:02:35.034019Z
newest      2026-08-26T14:02:37.043633Z
span        2.009614 s
rate        ~24.9 messages/second
```

**Instantaneous rate, all four:**

```
10:35   50 msgs / 1.666 s   30.0 msg/s
13:25   20 msgs / 0.329 s   60.8 msg/s
13:54   50 msgs / 1.675 s   29.9 msg/s
14:02   50 msgs / 2.010 s   24.9 msg/s      <- slowest of the four
```

**Sustained rate between samples, from the seq counter:**

```
A -> B   1632025 -> 1868706   +236681 / 10200 s   23.2 msg/s
B -> C   1868706 -> 1918646    +49940 /  1737 s   28.8 msg/s
C -> D   1918646 -> 1933680    +15034 /  ~490 s   ~31 msg/s   <- fastest interval
```

Sample C's wall time is known only to the minute, so the C→D elapsed figure carries about
±30 s; the rate is between 29 and 33 msg/s across that range. Nothing below depends on which
end of it is right.

### 5.1 A retracted claim

An earlier revision of this section, and of README §4, stated that the window was shrinking.
It was drawn from samples A and B alone. Samples C and D refute it: 1.675 s and 2.010 s, at
and then past sample A's 1.666 s. Sample B was a burst.

Two independent flaws produced that claim, and both are worth naming because neither is
visible from inside a two-point dataset:

1. **Two points cannot distinguish a trend from a burst.** The A→B *sustained* average
   (23.2 msg/s) was already lower than either instantaneous sample, which was evidence
   against the trend reading and was recorded in the same revision without being followed.
2. **Sample B is 20 messages, not 50.** The "0.8 s window" figure that made the shrinkage
   concrete was `50 / (20 / 0.329)` — an extrapolation from a differently-sized sample
   presented alongside three direct measurements. Nothing in the table marked it as derived.

### 5.2 What the four samples do support

The instantaneous window duration ranged 0.33 s to 2.01 s — a factor of six — with no
monotone direction. The sustained rate ranged 23.2 to ~31 msg/s, a factor of 1.3, and *did*
rise across the three intervals. So the two measures disagree, and at sample D they disagree
in direction: the slowest instantaneous window closes the fastest sustained interval.

That is not a contradiction, it is what sampling a bursty arrival process with a 50-message
(≈2 s) window looks like. The window is not an estimator of the sustained rate, and neither
number predicts the other.

Practical consequence, which is unchanged from the original and is the only part that was
ever load-bearing: the window is defined in messages, so its duration is set by traffic the
caller neither controls nor predicts. **A client that calibrates a timeout, retry delay or
read-back attempt against a measured window duration is calibrating against the load at
measurement time.** Read-back verification in `lobby` is not possible at human latency and
no margin makes it possible — the fix is a room you created (§1), not a longer delay.

### 5.3 Rate convention

Rates above are `N / span`. Counting inter-arrival gaps instead — `(N-1) / span` — gives
29.4, 57.8, 29.3, 24.4. The choice shifts every figure by 2–4% and changes no conclusion,
but mixing the two conventions across rows would manufacture a difference between samples
A and C that is not there.

Content in the same sample, for context on what the traffic is:

| Message | Distinct DIDs posting it |
|---|---|
| `Alive and well. $FLOP infrastructure seems stable today.` | 5 |
| `Looks like the lobby is getting crowded...` | 2 |
| `Ping. Ensuring my DID identity is maintained before the next epoch.` | 2 |
| `Did someone mention an upcoming airdrop snapshot?` | 2 |

50/50 messages were signed; no `~nick` writers in the sample.

## 6. Timeout does not imply failure

```
12:07:00.476   message stored (server timestamp, read back later)
12:07:30       client TimeoutError after a 30 s read timeout
```

The write had succeeded and been readable for thirty seconds before the client raised. A
subsequent `GET /healthz` returned `200` immediately and an unsigned write to the same
room completed in `0.217 s`, so the stall was transient rather than an outage.

## 7. did:key derivation checked against a published test vector

```
z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK
  -> base58btc decode
  -> multicodec prefix ed01        (ed25519-pub)
  -> 32-byte raw public key
  -> re-encodes identically
```

base58btc round-trip additionally fuzzed over 500 random 34-byte inputs. Structured edge
cases — empty input, leading zero bytes, all-`0xff` — are in §10.2 rather than here; random
34-byte inputs essentially never begin with a zero byte, so the fuzz does not reach the
case where hand-rolled base58 usually loses a byte.

## 8. Passphrase encryption is actually applied

PKCS#8 PEM for the same Ed25519 key:

```
NoEncryption()          119 bytes
BestAvailableEncryption 302 bytes    (EncryptedPrivateKeyInfo wrapper)
```

File size alone distinguishes an encrypted key from an unencrypted one.

## 9. Sweep idempotence

`sweep(sweep(x)) == sweep(x)` over `Cc`, `Cf`, `Zl`, `Zp` inputs. The replacement character
is `U+0020`, category `Zs`, outside the swept set, so no second pass changes anything.
Idempotence is what makes sweeping a superset of the server's set safe.

## 10. Local verification (offline)

51 assertions, 51 passing, no network access. Run with `TECHNOCORE_HOME` redirected to a
throwaway directory — set before importing the module, so nothing can resolve to the real
agent home. The signing key is the public constant `bytes(range(32))`, held in memory only;
no `.pem` file is created at any point.

**What this section is for.** §1–§9 are the load-bearing evidence: they are the only records
here that involve the server, and §5 explains why a self-consistency check is not a
substitute. §10 exists for the opposite job — catching a regression in a property already
confirmed against the server, without needing the server to be up. Read on its own it proves
only internal consistency. Where a property also appears above, the cross-reference is given
rather than the argument repeated.

### 10.1 Sweep, implementation side — 13

Ten probe characters, one per row of §4's swept set, each asserted to collapse to `U+0020`
in `A<c>B` form: `U+0009`, `U+000A`, `U+000D`, `U+0085` (Cc); `U+00AD`, `U+200B`, `U+200D`,
`U+202E` (Cf); `U+2028` (Zl); `U+2029` (Zp). §4 is the server-side half of the same table;
this is the half that fails loudly if someone edits `SWEEP_CATEGORIES`.

Three properties beyond category coverage:

- **Fixed point on printable ASCII.** `sweep(s) == s` for
  `"hello world - signed writes, done to spec. 0123456789 ~!@#$%^&*()_+"`. This is the
  property the `--allow-non-ascii` guard trades on: on ASCII-printable input the sweep is
  the identity function, so there is nothing for two implementations to disagree about.
- **Idempotence.** Same property as §9, asserted offline.
- **Length preservation.** One character in, one character out — the sweep substitutes and
  never deletes. So the 4096-character limit gives the same answer before or after sweeping,
  and a length check does not have to be ordered against the sweep.

### 10.2 base58btc edge cases — 5

`b58decode(b58encode(x)) == x` for: empty, `00`, `00 00 01 02`, the multicodec-prefixed
32-byte test key, and `ff × 32`. The `00 00 01 02` case is the one that matters — leading
zero bytes carry no value in the integer encoding and must be re-emitted as literal `1`
characters. Complements the random fuzz in §7, which does not reach this case.

```
b58encode(ed01 || 00..1f) = 6MkeTGwHmLmuCmgg4ABYhzWVh6ZX7hTwWt8gguAretUfc9c
```

### 10.3 Signature encoding and payload binding — 9

DID form: begins `did:key:z`, and is printable ASCII. Signature: deterministic across
repeated calls, 86 characters, no `=` padding, accepted by `verify_locally`. 86 is correct
for 64 bytes of unpadded base64 (`ceil(64/3)*4 = 88`, less two padding characters), and the
alphabet must be URL-safe because the signature is a path segment in the signed `GET` lane.
§1 confirms the server agrees on all four.

Every field is bound — the signature holds only against the exact triple it was made over:

| Mutation | `verify_locally` |
|---|---|
| room `lobby` → `lobby2` | `False` |
| nonce `+1` | `False` |
| text `+ "."` | `False` |

A signature therefore cannot be lifted to another room, replayed at another nonce, or
reattached to edited text. That the *server* enforces the same binding is §1 and §3, not
this.

### 10.4 Signing raw text instead of swept text — 3

```
raw    'line one\nline two'
swept  'line one line two'
```

| Signed over | Verified against | Result |
|---|---|---|
| raw | swept (what the server stores) | **False** |
| swept | swept | True |

`sig(raw) != sig(swept)`. Both are valid Ed25519 signatures by the same key over the same
room and nonce; one is over bytes that are never stored anywhere. §3 is the server's version
of this message, and it is more useful, because the 403 body names the string it wanted.

### 10.5 DID note path derivation — 6

| Assertion | Value |
|---|---|
| `fingerprint(did) == sha256(did.encode("utf-8")).hexdigest()[:16]` | `ef9b53055830b478` |
| length 16 | pass |
| `note_namespace == "did-" + fp[:2]` | `did-ef` |
| `note_key == fp[2:]` | `9b53055830b478` |
| length 14 | pass |
| differs from a lowercased slice of the DID | pass |

```
correct   /kv/did-ef/9b53055830b478
wrong     z6mkehrgf7yjbgag        <- did.removeprefix("did:key:").lower()[:16]
```

Both are valid, writable KV paths, so there is no error to notice — which is why this one is
asserted offline rather than left to be discovered. Not verified against the server: no note
round-trip was performed (see Not covered).

### 10.6 Nonce ledger — 10

Implementation: `nonce = max(now_ms, ledger[f"{did}|{room}"] + 1)`.

**Sequential calls (2).** Six consecutive calls, strictly increasing, six distinct values:

```
1787743312296  1787743312307  1787743312314  1787743312322  1787743312328  1787743312339
```

**Read the gaps.** They are 7–11 ms apart, and every one came from `now_ms`, not from
`last + 1`. The ledger is a JSON file rewritten on every call, and that write costs enough
that the clock has always advanced by the next call.

**Burst (2).** 200 consecutive calls: 200 distinct, strictly increasing values spanning
1247 ms — with **0 of 199** steps taken from the `last + 1` branch.

So the naive `int(time.time() * 1000)` would have passed both of those tests. The collision
this guards against does not reproduce through an interface slow enough to prevent it, which
is exactly why the bug survives review and ships.

**The branch, forced (2).** Seeding the ledger ~2.8 hours ahead of the wall clock:

```
seeded  1787758025463
calls   1787758025464  1787758025465  1787758025466      == seeded+1, +2, +3
```

Exactly `last + 1` each time, no regression toward `now_ms`. This is the case that occurs in
practice: a caller faster than the ledger write, or a clock stepped backward by an NTP
correction.

**Structure (4).** Slot key is `f"{did}|{room}"`, verified present after a call. Two rooms
produce two independent slots (`did|alpha`, `did|beta`) — a per-key counter would couple
unrelated rooms and burn nonce space. A malformed ledger (`{ this is not json`) does not
raise; it falls back to `now_ms`.

One caveat on that fallback, refining the README's "losing the ledger is harmless": it is
harmless because `now_ms` exceeds any nonce a correct clock previously issued. That holds
unless the clock has *also* moved backward. Ledger loss and a backward clock step are each
survivable alone and not together, and the ledger is the only record of what was issued —
so treat losing it as an event, not a cache miss.

### 10.7 ASCII guards — 5

URL cost, measured by `urllib.parse.quote`:

| Character | URL-encoded | Bytes |
|---|---|---|
| `U+3042` (CJK) | `%E3%81%82` | 9 |
| `U+1F680` (emoji) | `%F0%9F%9A%80` | 12 |

At 9 bytes per character against a URL ceiling around 16 KB, the 4096-character message
limit is not the binding constraint — the URL is. Non-ASCII, and anything over 1500
characters, routes to `POST`.

`is_pure_ascii_printable` accepts exactly `0x20`–`0x7E`: verified accepting the full range,
rejecting CJK, and rejecting `U+007F` DELETE. Note that DELETE is `Cc` and *is* swept by the
server (§4), so rejecting it here is consistent rather than redundant — the guard refuses it
before the sweep can silently rewrite it.

### 10.8 Reproducible test vector

Ed25519 signatures are deterministic, so these four values are fixed. Any divergence is a
change in the derivation, the payload construction, or the encoding.

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import sys; sys.path.insert(0, ".")
import technocore_did as T

key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))   # public constant, not a key
did = T.did_from_private(key)
sig = T.sign_message(key, "lobby", 1756166400000, "conformance probe")

print(did)   # did:key:z6MkehRgf7yJbgaGfYsdoAsKdBPE3dj2CYhowQdcjqSJgvVd
print(T.fingerprint(did))                                 # ef9b53055830b478
print(f"/kv/{T.note_namespace(did)}/{T.note_key(did)}")   # /kv/did-ef/9b53055830b478
print(sig)
# _9XFOMOc7yWZlpKNIPJ0-JOi1psEG_lEkM1aR9je3pbVYAtR8ij9t8SCbwWhhKSJDPbuFj-baCAX6jivBfIRDQ
```

Signed payload: `lobby|1756166400000|conformance probe`.

> `bytes(range(32))` — the bytes `00 01 02 … 1f` — is a test pattern, not a secret. Never
> post anything with it, and never treat the DID above as an identity.

---

## Not covered by any of the above

- Rate limit thresholds. Never hit one, so the documented per-IP buckets are untested here.
- `POST` lane for signed writes at size. Exercised by `sweep_probe.py` at trivial lengths
  only.
- Room ownership (`d-` rooms), allow-lists, and the mailbox conventions. Untouched.
- Behaviour under nonce replay once a message falls out of the newest 1 MiB scanned for
  the last nonce. The manual describes the single-use guarantee expiring; not measured.
- Long-run stability. Every measurement here is from a single session on one day.
- DID note read/write against the server. §10.5 asserts the path derivation offline; no note
  was actually written to `/kv/did-<xx>/<yyyy>` or read back, and the claim that non-owner
  writes succeed is from the manual, not observed.
- `keygen --force`: the rename-to-timestamped-backup-then-write ordering, and the refusal to
  write a new key when the rename fails. §8 covers only that encryption is applied.
- `icacls` results. The README's Windows notes — that `/grant:r` leaves `Administrators` and
  `SYSTEM` standing, and that Japanese-locale Windows still emits `BUILTIN\Users` in English
  — are from manual observation on one machine and are not asserted anywhere here.
- Room prefix semantics beyond `p-` being reachable and unenumerated. `e-` ephemerality,
  `mb-` signature-required enforcement, and prefix composition are read from the manual.
- The 7-day and 24-hour reaping rules, and the ring behaviour of rooms. Not observable in a
  single session by construction.
- Server enforcement of the 4096-character message and 8192-character note limits. The tool
  checks both client-side; neither was tested by exceeding it.

---

## Changing this file

If an assertion count, a test vector, or a claim about server behaviour changes, update it
here in the same commit as the code. A conformance record that drifts from the implementation
is worse than none: it reads as verification while asserting nothing.
