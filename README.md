# Real Random Simulator

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

A coin, a pair of dice and a BIP-39 seed generator that draw on the OS CSPRNG,
extract from it **without bias**, and then **measure** the result with an exact test
battery instead of asserting that it is random.

| tab | what it draws | outcome space |
|---|---|---|
| **Coin** | 4 rounds × 64 tosses = 256 tosses | (2<sup>64</sup>)<sup>4</sup> = **2<sup>256</sup>** |
| **Dice** | 6 rounds × 6 dice = 36 rolls | (6<sup>6</sup>)<sup>6</sup> = **6<sup>36</sup>** |
| **BIP-39** | 12 / 15 / 18 / 21 / 24-word phrases, 9 chains derived | up to 2<sup>256</sup> |
| **About** | version, licence, the GPL in full | — |

tkinter GUI. No third-party packages, no network, no telemetry. **Double-click
`real_random_simulator.bat`** on Windows, or:

```
python real_random_simulator.py
```

### The files

```
rrs_kernel.py              shared kernel - REQUIRED, the program will not start without it
real_random_simulator.py   Coin / Dice / BIP-39 / About
real_random_simulator.bat  Windows launcher
LICENSE                    GNU GPL v3, verbatim
README.md
.gitignore
```

Keep `rrs_kernel.py` beside the `.py` — the program checks for it before it even
looks for an interpreter, and names it if it is missing.

### What lives in the kernel

`rrs_kernel.py` holds everything that is not specific to one tab: the four entropy
sources and the `Engine` (SHA-512 counter-mode DRBG, byte accounting, rejection
sampling), the whole statistics stack (`chi2_sf`, `runs_test`, serial pairs,
Miller–Madow entropy, exact binomial p-values), the colour palette, the CJK-capable
font resolution, the canvas drawing helpers, the scrollable-page widget, the stats
table, the About tab, and the `KernelApp` window base class.

One consequence worth knowing if you fork it: fonts cannot be resolved until a Tk
root exists, so the kernel resolves them at window creation and then **pushes** the
chosen families back into whichever module imported it (`register_fonts`). That is
why the program calls `rrs_kernel.register_fonts(globals())` at the top — without
it the importing module keeps drawing with the placeholder families.

### The launcher

`real_random_simulator.bat` finds a working interpreter in this order — the `py`
launcher, `python` on PATH, then the usual install folders — and **only accepts one that can actually
`import tkinter`**, so a Python built without it is skipped rather than picked and
silently failing. It then starts the app detached with `pythonw`, so the console
closes and only the program window stays.

Before any of that it checks that both `real_random_simulator.py` *and*
`rrs_kernel.py` are sitting beside it, and names whichever one is missing — a missing
kernel gets its own message rather than a Python traceback.

If anything goes wrong:

```
real_random_simulator.bat debug
```

keeps the console open, prints which interpreter it chose, and shows the full
traceback and exit code. The app also carries a top-level handler that pops the
traceback up in a window — under `pythonw` there is no console, so a startup fault
would otherwise look like "nothing happened".

The launcher is pure ASCII (no code-page surprises), CRLF, quotes every path, and
reads or writes nothing in the folder besides launching the `.py` beside it.

---

## Tabs 1 & 2 — how big the outcome space actually is

### Coin — 4 rounds × 64 tosses = 256 tosses

| | |
|---|---|
| per round | 2<sup>64</sup> = **18,446,744,073,709,551,616** |
| four rounds | (2<sup>64</sup>)<sup>4</sup> = **2<sup>256</sup>** |
| exact | 115,792,089,237,316,195,423,570,985,008,687,907,853,269,984,665,640,564,039,457,584,007,913,129,639,936 |
| approx | 1.1579 × 10<sup>77</sup>  (78 digits) |

Yes — your 2<sup>64</sup>×2<sup>64</sup>×2<sup>64</sup>×2<sup>64</sup> is right, and it collapses to 2<sup>256</sup>.
That is the same size as a SHA-256 output space or a Bitcoin private key space. For
scale, the observable universe holds roughly 10<sup>80</sup> atoms, so one draw here
picks out one item from a set about a thousandth the size of every atom in the sky.

### Dice — 6 rounds × 6 dice = 36 rolls

| | |
|---|---|
| per round | 6<sup>6</sup> = **46,656** |
| six rounds | (6<sup>6</sup>)<sup>6</sup> = **6<sup>36</sup>** |
| exact | 10,314,424,798,490,535,546,171,949,056 |
| approx | 1.0314 × 10<sup>28</sup>  (29 digits) |

Note 6<sup>36</sup> is *not* 36<sup>6</sup>. Six rounds of six dice multiply the exponents,
they don't multiply the base.

The app computes both numbers at runtime with exact Python integers and prints the
full value — nothing is hardcoded or rounded.

---

## Tab 3 — BIP-39 seed phrases

> **These are real, spendable keys.** A phrase generated on a general-purpose PC is
> not as safe as one generated inside a hardware wallet's secure element — this
> machine has an OS, a screen buffer, a clipboard and probably a network. Use the tab
> to learn the mechanism and to cross-check that a device and the standard agree. For
> a wallet you intend to fund, generate on the device itself.

### A correction worth stating plainly

The usual diagram says 12 words give `2048^12 = 2^132` combinations. That counts
*word sequences*, not *valid mnemonics*. Only 1 in 2<sup>4</sup> = 16 sequences
carries a correct checksum, so:

| Length | Entropy | Checksum | Total bits | Word sequences | **Valid phrases** |
|---|---|---|---|---|---|
| 12 | 128 | 4 | 132 | 2<sup>132</sup> | **2<sup>128</sup>** |
| 15 | 160 | 5 | 165 | 2<sup>165</sup> | **2<sup>160</sup>** |
| 18 | 192 | 6 | 198 | 2<sup>198</sup> | **2<sup>192</sup>** |
| 21 | 224 | 7 | 231 | 2<sup>231</sup> | **2<sup>224</sup>** |
| 24 | 256 | 8 | 264 | 2<sup>264</sup> | **2<sup>256</sup>** |

The security is the entropy, never more. **The checksum catches typing errors; it
adds no secrecy.** Everything else in your diagram is right: 2048 = 2<sup>11</sup>,
11 bits per word, 12 × 11 = 132.

Note the last row: **a 24-word phrase is 2<sup>256</sup> — the same space as the Coin
tab's 4 × 64 = 256 tosses.** That is not a coincidence, and the tab exploits it: the
**Use Coin tab tosses** button turns your 256 physical-style tosses into a 24-word
seed *bit for bit*, nothing hashed, nothing discarded, nothing added.

### What the tab does

- **Length dropdown** — 12 / 15 / 18 / 21 / 24 words
- **Entropy** from any of the four sources, or imported from the Coin tab, or from
  freshly rolled dice
- **Verify mode** — paste a phrase from a Ledger, Trezor, BitBox, KeepKey or Coldcard;
  it checks every word against the 2048-word list, recomputes the checksum and derives
  the same addresses, so you can confirm your device and this tool agree
- **Passphrase** (BIP-39 "25th word") and **account index**
- **Private keys hidden by default**; saved run files redact them unless you opt in

### Derived addresses

| Chain | Path | Curve |
|---|---|---|
| Bitcoin Legacy P2PKH | `m/44'/0'/0'/0/0` | secp256k1 |
| Bitcoin Nested SegWit | `m/49'/0'/0'/0/0` | secp256k1 |
| Bitcoin Native SegWit | `m/84'/0'/0'/0/0` | secp256k1 |
| Bitcoin Taproot | `m/86'/0'/0'/0/0` | secp256k1 |
| Ethereum (+ EVM) | `m/44'/60'/0'/0/0` | secp256k1 |
| Mina | `m/44'/12586'/0'/0/0` | **Pallas** |
| Solana | `m/44'/501'/0'/0'` | ed25519 |
| Aptos | `m/44'/637'/0'/0'/0'` | ed25519 |
| Sui | `m/44'/784'/0'/0'/0'` | ed25519 |

Pipeline: mnemonic → PBKDF2-HMAC-SHA512 (2048 rounds, salt `"mnemonic"`+passphrase)
→ 512-bit seed → BIP-32 (secp256k1) or SLIP-10 (ed25519) → private key → public key
→ address. Yes, exactly the chain you described.

### On the dice as a seed source

A die carries log2(6) = 2.585 bits, so the Dice tab's 36 rolls hold only **93 bits** —
not enough for even a 12-word phrase. Rather than quietly stretch them, the tab rolls
the number actually required (50 / 62 / 75 / 87 / 100 dice) and condenses with SHA-256,
the method Coldcard and the standard dice-entropy tools use.

---

## Why this is real random, not a probability cloud

**1. The source.** Default is the OS CSPRNG (`os.urandom` / `secrets`). On Windows
that is `BCryptGenRandom`, continuously reseeded from hardware entropy — interrupt
timing, and RDSEED/RDRAND where the CPU offers it. It is not a formula walking a
fixed orbit. Mersenne Twister is included as a *selectable mode* so you can put the
"fake random" side by side with the real thing and compare the test scores.

**2. The coin extraction is exactly fair.** One raw bit per toss, straight off the
byte stream. A bit is already uniform on {0,1}, so there is no room for bias.

**3. The dice extraction is exactly fair — this is the part most simulators get
wrong.** 6 is not a power of two. The naive `byte % 6` is *biased*: 256 = 42×6 + 4,
so faces 1–4 land 43/256 of the time and faces 5–6 only 42/256. This program uses
**rejection sampling** — any byte ≥ 252 is discarded and re-drawn. Of the 252
accepted values each face gets exactly 42, so every face is exactly 1/6. The stats
panel shows the live discard count against the theoretical 1.5625%.

**4. Nothing is asserted, everything is measured.** Every run is scored with a real
test battery and exact p-values.

---

## The four sources

| Mode | Keying | Reproducible |
|---|---|---|
| **OS entropy** | every byte from `os.urandom` | no |
| **OS entropy + your seed** *(default)* | SHA-512(seed ‖ 64 fresh OS bytes ‖ time_ns ‖ pid) → SHA-512 counter DRBG | no |
| **Your seed only** | SHA-512(seed) → SHA-512 counter DRBG | **yes** — same seed replays the identical run |
| **Mersenne Twister MT19937** | `random.Random(seed)`, or OS-seeded if the seed is blank | yes, when seeded |

Type a seed and press **Apply seed**. All four modes are consumed through the *same*
extraction code, so a comparison between them reflects only the source, never the
method. A key fingerprint is shown for every run so you can identify it later.

---

## Controls

| | |
|---|---|
| **Play / Resume** | run the animated sequence from the current position |
| **Pause** | stop where it is; Resume continues the same already-drawn value |
| **Fill rest** | complete every remaining cell instantly, no animation |
| **Retoss / Reroll** | clear everything back to the stopped default |
| **click a cell** | re-toss **only** that cell; the play cursor stays put |
| **shift+click a cell** | move the cursor there and play onward from it |
| **Speed** | 1 (slow) to 10 (fast) |
| **Copy values** | the whole draw to the clipboard |
| **Save run** | timestamped `.txt` into the `runs\` subfolder — source, seed, fingerprint, full draw, all statistics |

The grid starts empty and nothing moves until you press Play.
No entropy is drawn before then, and pausing mid-toss does not waste the bit that
was already drawn.

---

## The statistics panel

Rows carrying a **p-value are hypothesis tests** and are what the pass / marginal /
FAIL verdict refers to. Balance, counts and entropy are descriptive only.

- **Runs test (Wald–Wolfowitz)** — is the alternation rate right?
- **Chi-square goodness of fit** — df=1 for the coin, df=5 for the dice
- **Serial pair test** (coin, df=3) — are 00/01/10/11 equally common?
- **Adjacent changes** (dice) — exact two-sided binomial test, not a normal approximation
- **Longest run** — reported with the expected number of occurrences of a run that
  long, so a long streak can be judged instead of just eyeballed
- **Shannon entropy** — shown against the *small-sample expectation*, not just the
  maximum. At n=36 the plug-in estimate sits about 0.10 bits below log2(6) even for a
  perfectly fair die; comparing against the maximum alone would make a fair run look
  broken.

One 256-toss run will read "marginal" on roughly 1 test in 100 purely by chance.
That is what a fair coin looks like, not evidence of a fault.

---

## Verification

None of the claims above are asserted on trust. This is what was actually run.

### The kernel boundary

- `rrs_kernel.py` imports and reports its version **before any Tk root exists** —
  that is the case that would break if the kernel tried to resolve fonts at import
  time
- the importing module receives the resolved font families through
  `register_fonts` — asserted, not assumed
- after the split the numbers are unchanged: coin still draws 256 tosses from exactly
  32 bytes, and BIP-39 still returns `bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu`
  and `B62qpqCoBci3mKNrfCnLkKS2SSV9QyrPbPBABe4stVWnRRfkG8sn3t4` for the reference
  mnemonic
- the **About** tab was checked to carry GPL sections 15 and 16 verbatim and to load
  the full 35,149-byte licence from `LICENSE` beside the program
- every test suite passes against the split files

### The .bat launcher

No Windows shell was reachable from the machine this was built on, so rather than
eyeball the batch file it was run under a **real `cmd.exe`** via Wine, from a folder
path containing spaces to match a normal install. Every branch was executed:

- no Python at all → the help text, no syntax errors through the whole probe chain
- a real PE `python.exe` at a path *containing a space* → accepted; `PY` and `PYW`
  come out correctly quoted and `pythonw.exe` is derived right beside it
- `start` genuinely detaches and hands the script path through intact — verified by
  having the stub executable log the argv it received
- an interpreter that **fails** `import tkinter` → correctly rejected, falls through
  to the help instead of being used
- `debug` → runs in-console, reports the interpreter and exit code, pauses
- `.py` missing next to the launcher → clear message
- **`rrs_kernel.py` missing** → its own clear message, checked before the interpreter
  probe even starts

Two findings worth recording. The first test stub was itself a `.bat`, and `cmd`
transfers control to a child `.bat` without ever returning, so the probe appeared to
fail — a fault in the test, not the launcher; rebuilt as a real `.exe`, the logic was
correct. Separately, inserting the kernel check by string substitution corrupted the
file, because the anchor `:no_app` also matched inside the `goto :no_app` line. The
launcher was regenerated from a known-good copy and re-tested from scratch.


### BIP-39 and the nine chains

- the embedded wordlist hashes to **`2f5eed53…dbda`**, the SHA-256 of the official
  `english.txt`; the app re-derives that hash at startup, so a corrupted copy cannot
  go unnoticed
- all official **BIP-39 (Trezor) vectors** pass: entropy → mnemonic → seed, including
  the `TREZOR`-passphrase seeds
- all three **BIP-86 Taproot** spec vectors match exactly, as do the published
  BIP-44 / 49 / 84 addresses and the well-known Ethereum address for the canonical
  test phrase
- every one of the 9 chains was cross-checked against **`bip_utils`** on 6 random
  seeds across 128/192/256-bit entropy — 100% agreement
- **Mina** has no Python reference library, so its addresses were cross-checked
  against the official **`mina-signer`** JS library over 2 mnemonics × 2 accounts.
  Worth recording: Mina does *not* use the Pasta-spec generator (−1, 2) — it uses
  o1js's base point (1, 12418654782883325593414442427049395787963493412651469444558597405572177144507).
  The spec generator silently produces wrong addresses.
- **Keccak-256** and **RIPEMD-160** were written from scratch (hashlib ships neither
  usably) and match `pycryptodome` on **308 input lengths each**, including every
  sponge rate boundary (135/136/137, 271/272/273)
- 1000 random entropies round-trip mnemonic → entropy exactly, across all 5 lengths
- checksum rejection verified: wrong word, non-wordlist word, wrong count; and
  ~1 in 16 random 12-word sequences pass, as the 4-bit checksum requires
  (measured 118 of 2000)

### Coin and dice

The engine, the statistics and the GUI were all exercised headlessly:

- `chi2_sf` matches `scipy.stats.chi2.sf` to **1.4 × 10⁻¹⁴** relative error across
  df = 1, 2, 3, 5, 10, 35
- the exact binomial p-value matches `scipy.stats.binomtest` to **1.1 × 10⁻¹⁶**
  over every outcome for four (n, p) pairs
- the two-sided normal p-value matches scipy to 4.6 × 10⁻¹⁵
- the rejection sampler was proved uniform by enumerating **all 256 byte values**:
  exactly 42 per face, exactly 4 rejected (1.5625%) — and the naive `byte % 6` was
  confirmed to give the biased 43/43/43/43/42/42
- 600,000 draws per mode per die/coin, all passing chi-square and the runs test
- byte accounting is exact: 256 tosses consume exactly 32 bytes; dice bytes drawn
  equals 36 plus rejections
- reproducibility contract checked in both directions for all four modes
- the real Tk window was built and driven under Xvfb: play, pause, resume, fill,
  reset, single-cell re-toss, shift+click play-from, all four sources on both tabs,
  clipboard, save-run, all ten speeds — with the printed integers checked back
  against the grid contents

---

## Licence

**GNU General Public License, version 3 or later** (`GPL-3.0-or-later`). The full
text is in [`LICENSE`](LICENSE), and the app shows it in its **About** tab along with
the no-warranty disclaimer — GPLv3's own "How to Apply These Terms" says that where a
terminal program would print a short notice at startup, *"for a GUI interface, you
would use an 'about box'"*.

In short: run it for any purpose, study it, change it, redistribute it, charge for
doing so, use it commercially. What you pass on must carry this same licence, keep
the notices intact, and come with the corresponding source including your changes.
No added restrictions, no relicensing to proprietary terms. That summary binds
nothing — only `LICENSE` does.

The copyright line reads **Real Random Simulator contributors** rather than a
personal name. Copyright vests automatically either way; naming a holder matters only
if it ever has to be enforced, and it is one search-and-replace across `LICENSE`,
`rrs_kernel.py` and `real_random_simulator.py` whenever you want it.

### Running it anywhere

Nothing here is Windows-specific except the `.bat` convenience launcher. On Linux or
macOS:

```
python3 real_random_simulator.py
```

Python 3.8 or newer with tkinter. No third-party packages, no network access, no
telemetry. On Debian/Ubuntu tkinter is a separate package (`apt install python3-tk`);
the python.org installers for Windows and macOS already include it.

### What is not in the repository

`runs/` — your saved draws, which contain seeds and key fingerprints — is in
`.gitignore` and stays local. The folder is created on first **Save run**; nothing
else in your folder is read or written.
