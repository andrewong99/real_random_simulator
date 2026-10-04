# -*- coding: utf-8 -*-
#
# rrs_kernel - shared entropy, statistics and UI kernel for the Real Random
# Simulator family of programs.
# Copyright (C) 2026 Real Random Simulator contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Shared kernel for the Real Random Simulator.

Everything here is independent of any one tab, so a program built on it gets
the entropy, the statistics and the visual language as ONE implementation
rather than a copy that can drift.

What lives here: the palette and fonts, the four entropy sources (Engine), the
statistics battery with exact p-values, the scrollable page container, the
stats table widget, the About tab that carries the GPL notice, and KernelApp -
the Tk root that applies the theme and routes the mouse wheel.

Keep this file beside the program. It will not start without it.

FONTS: the usable font families are only knowable once a Tk root exists, so UI
and MONO start as Tk's defaults and are replaced when KernelApp is created.
A module that does `from rrs_kernel import *` binds its own copy of those two
names, so each such module calls register_fonts(globals()) and KernelApp then
writes the resolved families back into it. Without that the importing module
would keep drawing with the placeholder families.
"""

import hashlib
import math
import os
import random
import sys
import time
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

KERNEL_VER = "1.1"

__all__ = [
    "KERNEL_VER",
    "BG", "CARD", "PANEL", "EDGE", "TEXT", "MUTED", "DIM", "UP_C", "DOWN_C",
    "DIE_C", "PIP_C", "GOOD", "WARN", "BAD", "ACCENT",
    "UI", "MONO", "register_fonts",
    "MODE_OS", "MODE_OS_SEED", "MODE_SEED", "MODE_MT", "MODES", "MODE_NOTE",
    "Engine",
    "chi2_sf", "z_two_sided", "shannon_bits", "expected_sample_entropy",
    "binom_two_sided_p", "longest_run", "expected_run_occurrences",
    "count_runs", "runs_test", "chi2_uniform", "serial_pair_test",
    "verdict_colour", "sci", "grouped",
    "rounded_rect", "PIPS", "draw_die", "ease_out",
    "Scrollable", "StatsTable", "KernelApp",
    "COPYRIGHT", "LICENSE_NAME", "LICENSE_SPDX", "LICENSE_URL",
    "WARRANTY_NOTICE", "CONDITIONS_NOTICE", "find_license_text", "AboutTab",
]


# ----------------------------------------------------------------------------
# Licence
#
# GPLv3's own "How to Apply These Terms" says that where a terminal program
# would print a short notice at startup, "for a GUI interface, you would use
# an 'about box'". AboutTab below is that about box, and it is built here so
# every program in the family carries the same one.
#
# WARNING is sections 15 and 16 of the licence, copied verbatim -- this is the
# "show w" half, and it has to be exact, so it is embedded rather than
# summarised. The "show c" half is the full licence text, which is read from
# the LICENSE file beside the program when it is there and otherwise pointed
# to at gnu.org. Nothing here is a substitute for the licence; it is a pointer
# into it.
# ----------------------------------------------------------------------------
COPYRIGHT = "Copyright (C) 2026 Real Random Simulator contributors"
LICENSE_NAME = "GNU General Public License, version 3 or later"
LICENSE_SPDX = "GPL-3.0-or-later"
LICENSE_URL = "https://www.gnu.org/licenses/gpl-3.0.html"

WARRANTY_NOTICE = """\
  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES."""

CONDITIONS_NOTICE = """\
You may copy, distribute and modify this program under the terms of the GNU
General Public License, version 3 or (at your option) any later version. In
outline, and subject to the full text, that means:

  *  You may run it for any purpose, study how it works and change it.
  *  You may redistribute copies, with or without changes, charge for the
     service of doing so, and use it commercially.
  *  Whatever you distribute must come with this same licence, must keep the
     copyright and licence notices intact, and must carry the corresponding
     SOURCE CODE -- including your changes, with the changes marked and dated.
  *  You may not add further restrictions, and you may not relicense it under
     a proprietary or incompatible licence.
  *  The licence grants no trademark rights and, under section 11, passes on
     a patent licence from each contributor for their own contribution.

That outline is a reading aid and nothing more. Only the full text binds, and
the full text is on the next card."""


def find_license_text():
    """The verbatim licence, if a copy was shipped beside the program.

    Looked for next to this kernel and next to the running script, under the
    names a source tree actually uses. Returns (text, path) or (None, None) --
    a program that is run from a single downloaded .py has no LICENSE beside
    it, and the about box falls back to the gnu.org URL.
    """
    names = ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "COPYING.txt",
             "gpl-3.0.txt")
    roots = []
    for base in (__file__, getattr(sys.modules.get("__main__"), "__file__", None)):
        if not base:
            continue
        d = os.path.dirname(os.path.abspath(base))
        if d not in roots:
            roots.append(d)
    for d in roots:
        for n in names:
            p = os.path.join(d, n)
            try:
                if os.path.isfile(p):
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        body = fh.read()
                    # Guard against picking up some unrelated file called
                    # LICENSE: it has to actually be the GPL.
                    if "GNU GENERAL PUBLIC LICENSE" in body:
                        return body, p
            except OSError:
                pass
    return None, None


# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
BG = "#0f1218"
CARD = "#171c26"
PANEL = "#1e2531"
EDGE = "#2b3444"
TEXT = "#e7ebf3"
MUTED = "#8c96ad"
DIM = "#5d677c"
UP_C = "#f0b429"     # coin UP / gold
DOWN_C = "#4aa3df"   # coin DOWN / blue
DIE_C = "#e9edf5"    # die body
PIP_C = "#1a1f2b"    # die pips
GOOD = "#4ec98a"
WARN = "#f0b429"
BAD = "#ef6b6b"
ACCENT = "#6c8cff"

UI = "TkDefaultFont"
MONO = "TkFixedFont"


# ----------------------------------------------------------------------------
# Font resolution (see the module docstring for why this indirection exists)
# ----------------------------------------------------------------------------
_FONT_CONSUMERS = []


def register_fonts(module_globals):
    """Ask the kernel to push the resolved font families into this module."""
    _FONT_CONSUMERS.append(module_globals)


def _apply_fonts(ui, mono):
    global UI, MONO
    UI, MONO = ui, mono
    for g in _FONT_CONSUMERS:
        g["UI"], g["MONO"] = ui, mono


# ----------------------------------------------------------------------------
# Entropy sources
# ----------------------------------------------------------------------------
MODE_OS = "OS entropy  -  true random, NOT reproducible"
MODE_OS_SEED = "OS entropy + your seed  -  NOT reproducible"
MODE_SEED = "Your seed only  -  reproducible"
MODE_MT = "Mersenne Twister MT19937  -  PRNG, for comparison"
MODES = [MODE_OS, MODE_OS_SEED, MODE_SEED, MODE_MT]

MODE_NOTE = {
    MODE_OS: "Every byte comes straight from the OS CSPRNG (os.urandom). "
             "Hardware-seeded, no formula, cannot be replayed. Seed is ignored.",
    MODE_OS_SEED: "SHA-512 counter DRBG keyed from  SHA-512(seed || 64 fresh OS "
                  "entropy bytes || time_ns || pid).  Your seed contributes, but "
                  "the OS entropy makes each run unique.",
    MODE_SEED: "SHA-512 counter DRBG keyed from SHA-512(seed) only.  Fully "
               "deterministic - the same seed replays the identical run. Use this "
               "to audit or reproduce a result.",
    MODE_MT: "Python's random module: Mersenne Twister MT19937, a pure PRNG with "
             "a 19937-bit state and period 2^19937-1. Deterministic given its "
             "seed. This is the 'fake random' reference to compare against.",
}


class Engine:
    """Byte-stream random source with a selectable backend.

    Every mode is consumed through the SAME extraction code (bit reservoir for
    coins, rejection sampler for dice) so that a comparison between modes
    reflects only the source, never the extraction method.
    """

    def __init__(self, mode, seed_text=""):
        self.mode = mode
        self.seed_text = seed_text or ""
        self.bytes_drawn = 0
        self.rejected = 0
        self._bitbuf = 0
        self._bitcnt = 0
        self._buf = b""
        self._pos = 0
        self._ctr = 0
        self._key = b""
        self._mt = None

        seed_b = self.seed_text.encode("utf-8")

        if mode == MODE_OS:
            self.reproducible = False
            self.fingerprint = "n/a  (live OS entropy)"

        elif mode == MODE_OS_SEED:
            salt = (os.urandom(64)
                    + time.time_ns().to_bytes(8, "big")
                    + os.getpid().to_bytes(4, "big"))
            self._key = hashlib.sha512(b"RRS-v1|os+seed|" + seed_b + b"|" + salt).digest()
            self.reproducible = False
            self.fingerprint = hashlib.sha256(self._key).hexdigest()[:16]

        elif mode == MODE_SEED:
            self._key = hashlib.sha512(b"RRS-v1|seed|" + seed_b).digest()
            self.reproducible = True
            self.fingerprint = hashlib.sha256(self._key).hexdigest()[:16]

        elif mode == MODE_MT:
            if seed_b:
                self._mt = random.Random(seed_b)
                self.reproducible = True
                self.fingerprint = hashlib.sha256(b"RRS-v1|mt|" + seed_b).hexdigest()[:16]
            else:
                self._mt = random.Random(os.urandom(32))
                self.reproducible = False
                self.fingerprint = "n/a  (MT seeded from OS entropy)"
        else:
            raise ValueError("unknown mode: %r" % (mode,))

    # -- raw stream ---------------------------------------------------------
    def _refill(self):
        self._buf = hashlib.sha512(self._key + self._ctr.to_bytes(16, "big")).digest()
        self._pos = 0
        self._ctr += 1

    def next_byte(self):
        self.bytes_drawn += 1
        if self.mode == MODE_OS:
            return os.urandom(1)[0]
        if self.mode == MODE_MT:
            return self._mt.getrandbits(8)
        if self._pos >= len(self._buf):
            self._refill()
        b = self._buf[self._pos]
        self._pos += 1
        return b

    # -- unbiased extraction ------------------------------------------------
    def bit(self):
        """One fair bit. A raw bit is uniform on {0,1} by construction."""
        if self._bitcnt == 0:
            self._bitbuf = self.next_byte()
            self._bitcnt = 8
        self._bitcnt -= 1
        return (self._bitbuf >> self._bitcnt) & 1

    def die(self):
        """One fair die face 1..6 by rejection sampling.

        256 = 42*6 + 4.  Discarding 252..255 leaves 252 values, exactly 42 per
        face, so P(face) = 42/252 = 1/6 exactly.  `byte % 6` without this
        rejection would give faces 1-4 a probability of 43/256 and faces 5-6
        only 42/256 - a real, measurable bias.
        """
        while True:
            b = self.next_byte()
            if b < 252:
                return (b % 6) + 1
            self.rejected += 1


# ----------------------------------------------------------------------------
# Statistics  (exact p-values, no third-party dependency)
# ----------------------------------------------------------------------------
def _gser(a, x):
    """Series expansion for the regularised lower incomplete gamma P(a,x)."""
    ap = a
    s = 1.0 / a
    d = s
    for _ in range(4000):
        ap += 1.0
        d *= x / ap
        s += d
        if abs(d) < abs(s) * 1e-16:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gcf(a, x):
    """Continued fraction for the regularised upper incomplete gamma Q(a,x)."""
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 4000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-16:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def chi2_sf(x, k):
    """Upper tail probability  P(Chi2_k > x)."""
    if x <= 0:
        return 1.0
    a = k / 2.0
    xx = x / 2.0
    if xx < a + 1.0:
        return max(0.0, min(1.0, 1.0 - _gser(a, xx)))
    return max(0.0, min(1.0, _gcf(a, xx)))


def z_two_sided(z):
    """Two-sided p-value for a standard normal deviate."""
    return math.erfc(abs(z) / math.sqrt(2.0))


def shannon_bits(counts):
    n = sum(counts)
    if n <= 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / n
            h -= p * math.log2(p)
    return h


def expected_sample_entropy(k, n):
    """Small-sample expectation of the plug-in Shannon entropy.

    The plug-in estimator is biased LOW by roughly (k-1)/(2n) nats
    (Miller-Madow).  With only 36 rolls over 6 faces that bias is about 0.10
    bits, so comparing the measured value against log2(6) alone would make a
    perfectly fair run look deficient.  This is the honest reference point.
    """
    if n <= 0:
        return math.log2(k)
    return math.log2(k) - (k - 1) / (2.0 * n * math.log(2.0))


def binom_two_sided_p(x, n, p):
    """Exact two-sided binomial p-value by the method of small p-values.

    Sums the probability of every outcome no more likely than the observed
    one.  n is small here, so this is computed exactly rather than by a
    normal approximation.
    """
    if n <= 0 or not (0 < p < 1) or not (0 <= x <= n):
        return None
    px = math.comb(n, x) * p ** x * (1 - p) ** (n - x)
    tot = 0.0
    for i in range(n + 1):
        pi = math.comb(n, i) * p ** i * (1 - p) ** (n - i)
        if pi <= px * (1 + 1e-9):
            tot += pi
    return min(1.0, tot)


def longest_run(seq):
    best = 0
    cur = 0
    prev = object()
    for v in seq:
        cur = cur + 1 if v == prev else 1
        prev = v
        if cur > best:
            best = cur
    return best


def expected_run_occurrences(n, length, k):
    """Expected number of positions that start a run of >= `length` identical
    symbols, for n independent draws from k equally likely symbols.

    A given position starts such a run with probability (1/k)^(length-1): the
    first symbol is free, the next length-1 must match it.  There are
    n-length+1 eligible positions.
    """
    if length < 1 or n < length:
        return 0.0
    return (n - length + 1) * (1.0 / k) ** (length - 1)


def count_runs(seq):
    if not seq:
        return 0
    r = 1
    for i in range(1, len(seq)):
        if seq[i] != seq[i - 1]:
            r += 1
    return r


def runs_test(bits):
    """Wald-Wolfowitz runs test. Returns (R, E[R], sd, Z, p) or None."""
    n = len(bits)
    n1 = sum(bits)
    n0 = n - n1
    if n < 2 or n1 == 0 or n0 == 0:
        return None
    r = count_runs(bits)
    mu = (2.0 * n1 * n0) / n + 1.0
    var = (2.0 * n1 * n0 * (2.0 * n1 * n0 - n)) / (n * n * (n - 1.0))
    if var <= 0:
        return None
    sd = math.sqrt(var)
    z = (r - mu) / sd
    return r, mu, sd, z, z_two_sided(z)


def chi2_uniform(counts):
    """Chi-square goodness of fit against a uniform distribution."""
    k = len(counts)
    n = sum(counts)
    if n == 0 or k < 2:
        return None
    e = n / k
    x2 = sum((c - e) ** 2 for c in counts) / e
    df = k - 1
    return x2, df, e, chi2_sf(x2, df)


def serial_pair_test(bits):
    """Non-overlapping pair test on a bit sequence: 00/01/10/11, df=3."""
    m = len(bits) // 2
    if m < 4:
        return None
    counts = [0, 0, 0, 0]
    for i in range(m):
        counts[bits[2 * i] * 2 + bits[2 * i + 1]] += 1
    e = m / 4.0
    x2 = sum((c - e) ** 2 for c in counts) / e
    return counts, x2, 3, e, chi2_sf(x2, 3)


def verdict_colour(p):
    if p is None:
        return MUTED, ""
    if p >= 0.01:
        return GOOD, "pass"
    if p >= 0.001:
        return WARN, "marginal"
    return BAD, "FAIL"


def sci(n, sig=5):
    if n <= 0:
        return str(n)
    e = len(str(n)) - 1
    m = n / (10 ** e)
    return "%.*f x 10^%d" % (sig - 1, m, e)


def grouped(n):
    return format(n, ",")


# ----------------------------------------------------------------------------
# Canvas drawing helpers
# ----------------------------------------------------------------------------
# ============================================================================
# END OF BIP-39 / HD WALLET CORE
# ============================================================================

# ----------------------------------------------------------------------------
# Canvas drawing helpers
# ----------------------------------------------------------------------------
def rounded_rect(cv, x0, y0, x1, y1, r, **kw):
    r = min(r, (x1 - x0) / 2.0, (y1 - y0) / 2.0)
    pts = [
        x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
        x1, y1 - r, x1, y1, x1 - r, y1,
        x0 + r, y1, x0, y1, x0, y1 - r,
        x0, y0 + r, x0, y0,
    ]
    return cv.create_polygon(pts, smooth=True, **kw)


def _rot(cx, cy, x, y, a):
    dx, dy = x - cx, y - cy
    ca, sa = math.cos(a), math.sin(a)
    return cx + dx * ca - dy * sa, cy + dx * sa + dy * ca


PIPS = {
    1: [(0.0, 0.0)],
    2: [(-0.48, -0.48), (0.48, 0.48)],
    3: [(-0.48, -0.48), (0.0, 0.0), (0.48, 0.48)],
    4: [(-0.48, -0.48), (0.48, -0.48), (-0.48, 0.48), (0.48, 0.48)],
    5: [(-0.48, -0.48), (0.48, -0.48), (0.0, 0.0), (-0.48, 0.48), (0.48, 0.48)],
    6: [(-0.48, -0.55), (-0.48, 0.0), (-0.48, 0.55),
        (0.48, -0.55), (0.48, 0.0), (0.48, 0.55)],
}


def draw_die(cv, cx, cy, size, face, angle=0.0, body=DIE_C, pip=PIP_C,
             edge="#aab3c4", tags=None):
    """Draw a die of side `size` centred at (cx,cy), rotated by `angle` rad."""
    tags = tags or ()
    h = size / 2.0
    corners = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)]
    pts = []
    for (x, y) in corners:
        rx, ry = _rot(cx, cy, x, y, angle)
        pts.extend([rx, ry])
    cv.create_polygon(pts, fill=body, outline=edge, width=1.6,
                      joinstyle="round", tags=tags)
    pr = max(1.6, size * 0.085)
    for (ux, uy) in PIPS.get(face, []):
        px, py = cx + ux * h * 0.82, cy + uy * h * 0.82
        rx, ry = _rot(cx, cy, px, py, angle)
        cv.create_oval(rx - pr, ry - pr, rx + pr, ry + pr,
                       fill=pip, outline="", tags=tags)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 2


# ----------------------------------------------------------------------------
# Widgets
# ----------------------------------------------------------------------------
class Scrollable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Bg.TFrame")
        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, bd=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.inner = ttk.Frame(self.canvas, style="Bg.TFrame")
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)

    def _on_inner(self, _e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._sync_hsb()

    def _on_canvas(self, event):
        # Let the content stretch to the viewport when there is room, so a
        # horizontal scrollbar only appears when the content really is wider.
        self.canvas.itemconfigure(
            self._win, width=max(event.width, self.inner.winfo_reqwidth()))
        self._sync_hsb()

    def _sync_hsb(self):
        try:
            bbox = self.canvas.bbox("all")
            need = (bbox is not None
                    and (bbox[2] - bbox[0]) > self.canvas.winfo_width() + 2)
            if need and not self.hsb.winfo_ismapped():
                self.hsb.grid()
            elif not need and self.hsb.winfo_ismapped():
                self.hsb.grid_remove()
        except tk.TclError:
            pass

    def wheel(self, delta_units):
        self.canvas.yview_scroll(delta_units, "units")


# ----------------------------------------------------------------------------
# Base tab: shared control bar + playback state machine


class StatsTable(ttk.Frame):
    def __init__(self, parent, rows):
        super().__init__(parent, style="Panel.TFrame", padding=(14, 10))
        self.vars = {}
        self.vals = {}
        for r, key in enumerate(rows):
            ttk.Label(self, text=key[1], style="Key.TLabel").grid(
                row=r, column=0, sticky="w", pady=2, padx=(0, 16))
            v = tk.StringVar(value="-")
            lb = ttk.Label(self, textvariable=v, style="Mono.TLabel")
            lb.grid(row=r, column=1, sticky="w", pady=2)
            self.vars[key[0]] = v
            self.vals[key[0]] = lb
        self.columnconfigure(1, weight=1)

    def set(self, key, text, colour=None):
        self.vars[key].set(text)
        if colour:
            self.vals[key].configure(foreground=colour)
        else:
            self.vals[key].configure(foreground=TEXT)


# ----------------------------------------------------------------------------
# ABOUT TAB - the GPLv3 "about box"
# ----------------------------------------------------------------------------
class AboutTab(ttk.Frame):
    """Version, copyright, the no-warranty notice and the licence itself.

    GPLv3 asks an interactive program to make the licence and the disclaimer
    reachable from the interface; for a GUI that means an about box. This is
    a tab rather than a dialog so it is visible without being hunted for.
    """

    def __init__(self, parent, app_title, app_ver, blurb="", notes=()):
        super().__init__(parent, style="Bg.TFrame")
        self.scroll = Scrollable(self)
        self.scroll.pack(fill="both", expand=True)
        body = self.scroll.inner
        body.columnconfigure(0, weight=1)
        row = 0            # row inside `body`, one per card

        # ---- identity + the short notice ------------------------------------
        head = ttk.Frame(body, style="Card.TFrame", padding=(16, 14))
        head.grid(row=row, column=0, sticky="ew", padx=4, pady=(6, 8))
        head.columnconfigure(1, weight=1)
        row += 1

        hr = 0             # row inside `head`, counted separately
        ttk.Label(head, text=app_title, style="H2.TLabel").grid(
            row=hr, column=0, columnspan=2, sticky="w")
        hr += 1
        if blurb:
            tk.Label(head, text=blurb, bg=CARD, fg=MUTED, font=(UI, 9),
                     wraplength=900, justify="left").grid(
                row=hr, column=0, columnspan=2, sticky="w", pady=(2, 10))
            hr += 1

        for k, v in (
            ("version", "%s   (kernel %s)" % (app_ver, KERNEL_VER)),
            ("licence", "%s   [%s]" % (LICENSE_NAME, LICENSE_SPDX)),
            ("copyright", COPYRIGHT),
            ("full text", LICENSE_URL),
            ("running on", "Python %d.%d.%d   Tk %s   %s" % (
                sys.version_info[0], sys.version_info[1], sys.version_info[2],
                self._tk_version(), sys.platform)),
        ):
            ttk.Label(head, text=k, style="Key.TLabel").grid(
                row=hr, column=0, sticky="w", padx=(0, 18), pady=1)
            ttk.Label(head, text=v, style="Mono.TLabel").grid(
                row=hr, column=1, sticky="w", pady=1)
            hr += 1

        short = ("This program comes with ABSOLUTELY NO WARRANTY; for details "
                 "see\nthe disclaimer below. This is free software, and you "
                 "are welcome to\nredistribute it under certain conditions; "
                 "those are below too.")
        ttk.Label(head, text=short, style="Mono.TLabel", justify="left").grid(
            row=hr, column=0, columnspan=2, sticky="w", pady=(12, 0))

        # A note is either a string or (text, colour). These carry warnings
        # about real keys, so they are not drawn in the dim "footnote" grey.
        for note in notes:
            text, colour = note if isinstance(note, tuple) else (note, MUTED)
            n = ttk.Frame(body, style="Card.TFrame", padding=(16, 12))
            n.grid(row=row, column=0, sticky="ew", padx=4, pady=(0, 8))
            row += 1
            tk.Label(n, text=text, bg=CARD, fg=colour, font=(UI, 9),
                     wraplength=900, justify="left").pack(anchor="w")

        # ---- "show w" --------------------------------------------------------
        row = self._text_card(
            body, row, "No warranty  -  GPL sections 15 and 16, verbatim",
            WARRANTY_NOTICE, colour=WARN)

        # ---- "show c" --------------------------------------------------------
        row = self._text_card(
            body, row, "Your rights, and the conditions on them",
            CONDITIONS_NOTICE)

        text, path = find_license_text()
        if text:
            row = self._text_card(
                body, row,
                "GNU General Public License v3  -  full text, as shipped",
                text.rstrip(), mono=True, maxlines=34,
                footer="read from %s" % path)
        else:
            row = self._text_card(
                body, row, "GNU General Public License v3  -  full text",
                "No LICENSE file was found beside this program, so the full "
                "text is not\nbundled with this copy. It is at:\n\n    "
                + LICENSE_URL +
                "\n\nIf you received this program without the licence, "
                "whoever passed it on\nto you was obliged to include it.",
                colour=WARN)

    @staticmethod
    def _tk_version():
        try:
            return str(tk.TkVersion)
        except Exception:
            return "?"

    def _text_card(self, body, row, title, content, mono=True, colour=None,
                   maxlines=None, footer=None):
        card = ttk.Frame(body, style="Card.TFrame", padding=(16, 12))
        card.grid(row=row, column=0, sticky="ew", padx=4, pady=(0, 8))
        card.columnconfigure(0, weight=1)
        ttk.Label(card, text=title, style="H3.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8))

        lines = content.count("\n") + 1
        height = lines if maxlines is None else min(lines, maxlines)
        t = tk.Text(card, wrap="none" if mono else "word",
                    height=height, bd=0, highlightthickness=0,
                    bg=PANEL, fg=colour or TEXT,
                    font=(MONO if mono else UI, 9),
                    padx=12, pady=10, relief="flat",
                    insertbackground=TEXT,
                    selectbackground=ACCENT, selectforeground="#0b0e14")
        t.grid(row=1, column=0, sticky="ew")
        t.insert("1.0", content)
        # Read-only but still selectable, so the licence can be copied out.
        t.configure(state="disabled")

        if maxlines is not None and lines > maxlines:
            sb = ttk.Scrollbar(card, orient="vertical", command=t.yview)
            sb.grid(row=1, column=1, sticky="ns")
            t.configure(yscrollcommand=sb.set)
            # This pane scrolls on its own; don't also scroll the page under it.
            t.bind("<MouseWheel>",
                   lambda e: (t.yview_scroll(-1 if e.delta > 0 else 1, "units"),
                              "break")[1])
            t.bind("<Button-4>", lambda e: (t.yview_scroll(-1, "units"), "break")[1])
            t.bind("<Button-5>", lambda e: (t.yview_scroll(1, "units"), "break")[1])

        if footer:
            ttk.Label(card, text=footer, style="Note.TLabel").grid(
                row=2, column=0, sticky="w", pady=(6, 0))
        return row + 1


# ----------------------------------------------------------------------------
# The Tk root shared by both programs
# ----------------------------------------------------------------------------
class KernelApp(tk.Tk):
    """Applies the theme, carries the notebook, routes the wheel.

    A subclass sets up its own tabs and appends anything with a .stop() method
    to self.closeables so the window shuts down cleanly.
    """

    def __init__(self, title, subtitle, geometry="1280x880", minsize=(880, 600)):
        super().__init__()
        _apply_fonts(*self._pick_fonts())
        self.title(title)
        self.geometry(geometry)
        self.minsize(*minsize)
        self.configure(bg=BG)
        self._style()
        self.closeables = []

        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=14, pady=(12, 0))
        tk.Label(head, text=title.split("  ")[0], bg=BG, fg=TEXT,
                 font=(UI, 17, "bold")).pack(side="left")
        tk.Label(head, text="   " + subtitle, bg=BG, fg=MUTED,
                 font=(UI, 10)).pack(side="left", padx=(6, 0))
        self.flash_var = tk.StringVar(value="")
        tk.Label(head, textvariable=self.flash_var, bg=BG, fg=GOOD,
                 font=(UI, 9)).pack(side="right")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.bind_all("<MouseWheel>", self._wheel)
        self.bind_all("<Button-4>", lambda e: self._wheel(e, 1))
        self.bind_all("<Button-5>", lambda e: self._wheel(e, -1))
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._flash_after = None

    @staticmethod
    def _pick_fonts():
        try:
            fams = set(tkfont.families())
        except Exception:
            fams = set()
        ui = next((f for f in ("Segoe UI", "Inter", "Helvetica Neue",
                               "DejaVu Sans", "Arial") if f in fams), "TkDefaultFont")
        mono = next((f for f in ("Consolas", "Cascadia Mono", "DejaVu Sans Mono",
                                 "Menlo", "Courier New") if f in fams), "TkFixedFont")
        return ui, mono

    def _style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("Bg.TFrame", background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("Panel.TFrame", background=PANEL)
        s.configure("TSeparator", background=EDGE)

        s.configure("H2.TLabel", background=CARD, foreground=TEXT,
                    font=(UI, 11, "bold"))
        s.configure("H3.TLabel", background=CARD, foreground=TEXT,
                    font=(UI, 9, "bold"))
        s.configure("Key.TLabel", background=CARD, foreground=MUTED, font=(UI, 9))
        s.configure("Note.TLabel", background=CARD, foreground=DIM, font=(UI, 8))
        s.configure("Mono.TLabel", background=CARD, foreground=TEXT, font=(MONO, 9))
        s.configure("Mono2.TLabel", background=CARD, foreground=MUTED, font=(MONO, 8))
        s.configure("Big.TLabel", background=CARD, foreground=UP_C,
                    font=(MONO, 11, "bold"))
        s.configure("Face.TLabel", background=CARD, foreground=TEXT,
                    font=(UI, 13, "bold"))

        s.configure("Accent.TButton", background=ACCENT, foreground="#0f1218",
                    font=(UI, 9, "bold"), borderwidth=0, focuscolor=ACCENT,
                    padding=(16, 7))
        s.map("Accent.TButton",
              background=[("active", "#8aa4ff"), ("disabled", EDGE)],
              foreground=[("disabled", DIM)])
        s.configure("Ghost.TButton", background=PANEL, foreground=TEXT,
                    font=(UI, 9), borderwidth=0, focuscolor=PANEL, padding=(14, 7))
        s.map("Ghost.TButton",
              background=[("active", EDGE), ("disabled", CARD)],
              foreground=[("disabled", DIM)])

        s.configure("Dark.TEntry", fieldbackground=PANEL, foreground=TEXT,
                    bordercolor=EDGE, lightcolor=EDGE, darkcolor=EDGE,
                    insertcolor=TEXT, padding=5)
        s.configure("Dark.TCombobox", fieldbackground=PANEL, background=PANEL,
                    foreground=TEXT, arrowcolor=TEXT, bordercolor=EDGE,
                    lightcolor=EDGE, darkcolor=EDGE, padding=4)
        s.map("Dark.TCombobox",
              fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", TEXT)],
              selectbackground=[("readonly", PANEL)],
              selectforeground=[("readonly", TEXT)])
        self.option_add("*TCombobox*Listbox.background", PANEL)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", "#0f1218")

        s.configure("RO.TEntry", fieldbackground=PANEL, foreground=TEXT,
                    bordercolor=EDGE, lightcolor=EDGE, darkcolor=EDGE, padding=4)
        s.map("RO.TEntry",
              fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", TEXT)],
              bordercolor=[("readonly", EDGE)])
        s.configure("Dark.TCheckbutton", background=CARD, foreground=TEXT,
                    font=(UI, 9), focuscolor=CARD)
        s.map("Dark.TCheckbutton",
              background=[("active", CARD)],
              indicatorcolor=[("selected", ACCENT), ("!selected", PANEL)])

        s.configure("TNotebook", background=BG, borderwidth=0, tabmargins=(4, 4, 0, 0))
        s.configure("TNotebook.Tab", background=CARD, foreground=MUTED,
                    padding=(20, 10), borderwidth=0, font=(UI, 9, "bold"))
        s.map("TNotebook.Tab",
              background=[("selected", PANEL)],
              foreground=[("selected", TEXT)])

        # A scrollbar has to be findable. The old near-black-on-black thumb
        # hid the fact that these pages scroll at all, so content below the
        # fold was effectively invisible. Accent thumb, darker trough, wider.
        for _o in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
            s.configure(_o, background=ACCENT, troughcolor="#0b0e14",
                        bordercolor="#0b0e14", arrowcolor=TEXT,
                        darkcolor=ACCENT, lightcolor=ACCENT,
                        width=16, arrowsize=16, relief="flat")
            s.map(_o,
                  background=[("pressed", "#9db2ff"), ("active", "#8aa4ff")],
                  arrowcolor=[("pressed", "#ffffff"), ("active", "#ffffff")])
        s.configure("Horizontal.TScale", background=CARD, troughcolor=PANEL,
                    bordercolor=EDGE, darkcolor=ACCENT, lightcolor=ACCENT)

    def _current_tab(self):
        try:
            return self.nb.nametowidget(self.nb.select())
        except Exception:
            return None

    def _wheel(self, event, direction=None):
        tab = self._current_tab()
        # A tab exposes the page the wheel should move as .scroll; a tab with
        # its own sub-notebook returns whichever sub-page is showing, so the
        # wheel keeps working one level down.
        sc = getattr(tab, "scroll", None) if tab is not None else None
        if sc is None or not hasattr(sc, "wheel"):
            return
        if direction is None:
            direction = 1 if event.delta > 0 else -1
        sc.wheel(-3 * direction)

    def add_about_tab(self, app_title, app_ver, blurb="", notes=(),
                      label="ABOUT"):
        """Append the licence tab. Call it last, so it sits on the right."""
        self.about = AboutTab(self.nb, app_title, app_ver, blurb, notes)
        self.nb.add(self.about, text=label)
        return self.about

    def flash(self, msg):
        self.flash_var.set(msg)
        if self._flash_after:
            try:
                self.after_cancel(self._flash_after)
            except Exception:
                pass
        self._flash_after = self.after(4000, lambda: self.flash_var.set(""))

    def _close(self):
        for t in self.closeables:
            try:
                t.stop()
            except Exception:
                pass
        self.destroy()
