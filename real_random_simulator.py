#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Real Random Simulator - coin, dice and BIP-39 entropy from a real CSPRNG,
# measured with an exact test battery rather than asserted.
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
===============================================================================
 REAL RANDOM SIMULATOR                                 real_random_simulator.py
===============================================================================

 Three working tabs, all driven by genuine entropy and all measured rather
 than asserted, plus an About tab carrying the licence.

 TAB 1 - COIN  (up / down)
     4 rounds x 64 tosses = 256 tosses -> (2^64)^4 = 2^256
     = 115,792,089,237,316,195,423,570,985,008,687,907,853,269,984,665,
       640,564,039,457,584,007,913,129,639,936   (~1.1579 x 10^77)

 TAB 2 - DICE
     6 rounds x 6 dice = 36 rolls -> (6^6)^6 = 6^36
     = 10,314,424,798,490,535,546,171,949,056   (~1.0314 x 10^28)

 TAB 3 - BIP-39
     12 / 15 / 18 / 21 / 24 word seed phrases, checksum validated, with the
     keys and addresses for nine chains derived from them.

 HOW THE RANDOMNESS IS KEPT HONEST
     Source: the OS CSPRNG by default (BCryptGenRandom on Windows), optionally
     mixed with a seed you type. Mersenne Twister is selectable purely so you
     can compare a real source against a PRNG.
     Coin: one raw bit per toss - a bit is already uniform, so no bias is
     possible.
     Dice: rejection sampling. 256 = 42*6 + 4, so the naive byte % 6 favours
     faces 1-4; bytes >= 252 are discarded instead, making every face exactly
     1/6. The discard count is shown live.
     Everything is then scored with a real test battery and exact p-values.

 Requires: Python 3.8+ with tkinter, and rrs_kernel.py beside this file.
 No third-party packages, no network.
===============================================================================
"""

import hashlib
import hmac
import math
import os
import sys
import unicodedata
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from rrs_kernel import *                    # noqa: F401,F403
import rrs_kernel as _kernel

_kernel.register_fonts(globals())

APP_TITLE = "Real Random Simulator"
APP_VER = "1.1"


# ============================================================================
# BIP-39 / HD WALLET CORE
# ----------------------------------------------------------------------------
# Everything below to the next banner is pure standard-library cryptography,
# implemented from the published specifications and checked against their
# official test vectors. No third-party packages, no network.
# ============================================================================

# ---------------------------------------------------------------------------
# BIP-39 English wordlist -- the official 2048-word list.
# SHA-256 of the canonical english.txt (newline separated, trailing newline):
#   2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda
# WORDLIST_SHA256 below re-derives that hash at import time from the words
# embedded here, so a corrupted copy cannot go unnoticed.
# ---------------------------------------------------------------------------
_WORDLIST_RAW = """
abandon ability able about above absent absorb abstract absurd abuse
access accident account accuse achieve acid acoustic acquire across act
action actor actress actual adapt add addict address adjust admit adult
advance advice aerobic affair afford afraid again age agent agree ahead
aim air airport aisle alarm album alcohol alert alien all alley allow
almost alone alpha already also alter always amateur amazing among amount
amused analyst anchor ancient anger angle angry animal ankle announce
annual another answer antenna antique anxiety any apart apology appear
apple approve april arch arctic area arena argue arm armed armor army
around arrange arrest arrive arrow art artefact artist artwork ask aspect
assault asset assist assume asthma athlete atom attack attend attitude
attract auction audit august aunt author auto autumn average avocado avoid
awake aware away awesome awful awkward axis baby bachelor bacon badge bag
balance balcony ball bamboo banana banner bar barely bargain barrel base
basic basket battle beach bean beauty because become beef before begin
behave behind believe below belt bench benefit best betray better between
beyond bicycle bid bike bind biology bird birth bitter black blade blame
blanket blast bleak bless blind blood blossom blouse blue blur blush board
boat body boil bomb bone bonus book boost border boring borrow boss bottom
bounce box boy bracket brain brand brass brave bread breeze brick bridge
brief bright bring brisk broccoli broken bronze broom brother brown brush
bubble buddy budget buffalo build bulb bulk bullet bundle bunker burden
burger burst bus business busy butter buyer buzz cabbage cabin cable cactus
cage cake call calm camera camp can canal cancel candy cannon canoe canvas
canyon capable capital captain car carbon card cargo carpet carry cart case
cash casino castle casual cat catalog catch category cattle caught cause
caution cave ceiling celery cement census century cereal certain chair
chalk champion change chaos chapter charge chase chat cheap check cheese
chef cherry chest chicken chief child chimney choice choose chronic chuckle
chunk churn cigar cinnamon circle citizen city civil claim clap clarify
claw clay clean clerk clever click client cliff climb clinic clip clock
clog close cloth cloud clown club clump cluster clutch coach coast coconut
code coffee coil coin collect color column combine come comfort comic
common company concert conduct confirm congress connect consider control
convince cook cool copper copy coral core corn correct cost cotton couch
country couple course cousin cover coyote crack cradle craft cram crane
crash crater crawl crazy cream credit creek crew cricket crime crisp
critic crop cross crouch crowd crucial cruel cruise crumble crunch crush
cry crystal cube culture cup cupboard curious current curtain curve cushion
custom cute cycle dad damage damp dance danger daring dash daughter dawn
day deal debate debris decade december decide decline decorate decrease
deer defense define defy degree delay deliver demand demise denial dentist
deny depart depend deposit depth deputy derive describe desert design desk
despair destroy detail detect develop device devote diagram dial diamond
diary dice diesel diet differ digital dignity dilemma dinner dinosaur
direct dirt disagree discover disease dish dismiss disorder display
distance divert divide divorce dizzy doctor document dog doll dolphin
domain donate donkey donor door dose double dove draft dragon drama drastic
draw dream dress drift drill drink drip drive drop drum dry duck dumb dune
during dust dutch duty dwarf dynamic eager eagle early earn earth easily
east easy echo ecology economy edge edit educate effort egg eight either
elbow elder electric elegant element elephant elevator elite else embark
embody embrace emerge emotion employ empower empty enable enact end endless
endorse enemy energy enforce engage engine enhance enjoy enlist enough
enrich enroll ensure enter entire entry envelope episode equal equip era
erase erode erosion error erupt escape essay essence estate eternal ethics
evidence evil evoke evolve exact example excess exchange excite exclude
excuse execute exercise exhaust exhibit exile exist exit exotic expand
expect expire explain expose express extend extra eye eyebrow fabric face
faculty fade faint faith fall false fame family famous fan fancy fantasy
farm fashion fat fatal father fatigue fault favorite feature february
federal fee feed feel female fence festival fetch fever few fiber fiction
field figure file film filter final find fine finger finish fire firm
first fiscal fish fit fitness fix flag flame flash flat flavor flee flight
flip float flock floor flower fluid flush fly foam focus fog foil fold
follow food foot force forest forget fork fortune forum forward fossil
foster found fox fragile frame frequent fresh friend fringe frog front
frost frown frozen fruit fuel fun funny furnace fury future gadget gain
galaxy gallery game gap garage garbage garden garlic garment gas gasp gate
gather gauge gaze general genius genre gentle genuine gesture ghost giant
gift giggle ginger giraffe girl give glad glance glare glass glide glimpse
globe gloom glory glove glow glue goat goddess gold good goose gorilla
gospel gossip govern gown grab grace grain grant grape grass gravity great
green grid grief grit grocery group grow grunt guard guess guide guilt
guitar gun gym habit hair half hammer hamster hand happy harbor hard harsh
harvest hat have hawk hazard head health heart heavy hedgehog height hello
helmet help hen hero hidden high hill hint hip hire history hobby hockey
hold hole holiday hollow home honey hood hope horn horror horse hospital
host hotel hour hover hub huge human humble humor hundred hungry hunt
hurdle hurry hurt husband hybrid ice icon idea identify idle ignore ill
illegal illness image imitate immense immune impact impose improve impulse
inch include income increase index indicate indoor industry infant inflict
inform inhale inherit initial inject injury inmate inner innocent input
inquiry insane insect inside inspire install intact interest into invest
invite involve iron island isolate issue item ivory jacket jaguar jar jazz
jealous jeans jelly jewel job join joke journey joy judge juice jump jungle
junior junk just kangaroo keen keep ketchup key kick kid kidney kind
kingdom kiss kit kitchen kite kitten kiwi knee knife knock know lab label
labor ladder lady lake lamp language laptop large later latin laugh laundry
lava law lawn lawsuit layer lazy leader leaf learn leave lecture left leg
legal legend leisure lemon lend length lens leopard lesson letter level
liar liberty library license life lift light like limb limit link lion
liquid list little live lizard load loan lobster local lock logic lonely
long loop lottery loud lounge love loyal lucky luggage lumber lunar lunch
luxury lyrics machine mad magic magnet maid mail main major make mammal man
manage mandate mango mansion manual maple marble march margin marine market
marriage mask mass master match material math matrix matter maximum maze
meadow mean measure meat mechanic medal media melody melt member memory
mention menu mercy merge merit merry mesh message metal method middle
midnight milk million mimic mind minimum minor minute miracle mirror misery
miss mistake mix mixed mixture mobile model modify mom moment monitor
monkey monster month moon moral more morning mosquito mother motion motor
mountain mouse move movie much muffin mule multiply muscle museum mushroom
music must mutual myself mystery myth naive name napkin narrow nasty nation
nature near neck need negative neglect neither nephew nerve nest net
network neutral never news next nice night noble noise nominee noodle
normal north nose notable note nothing notice novel now nuclear number
nurse nut oak obey object oblige obscure observe obtain obvious occur ocean
october odor off offer office often oil okay old olive olympic omit once
one onion online only open opera opinion oppose option orange orbit orchard
order ordinary organ orient original orphan ostrich other outdoor outer
output outside oval oven over own owner oxygen oyster ozone pact paddle
page pair palace palm panda panel panic panther paper parade parent park
parrot party pass patch path patient patrol pattern pause pave payment
peace peanut pear peasant pelican pen penalty pencil people pepper perfect
permit person pet phone photo phrase physical piano picnic picture piece
pig pigeon pill pilot pink pioneer pipe pistol pitch pizza place planet
plastic plate play please pledge pluck plug plunge poem poet point polar
pole police pond pony pool popular portion position possible post potato
pottery poverty powder power practice praise predict prefer prepare
present pretty prevent price pride primary print priority prison private
prize problem process produce profit program project promote proof property
prosper protect proud provide public pudding pull pulp pulse pumpkin punch
pupil puppy purchase purity purpose purse push put puzzle pyramid quality
quantum quarter question quick quit quiz quote rabbit raccoon race rack
radar radio rail rain raise rally ramp ranch random range rapid rare rate
rather raven raw razor ready real reason rebel rebuild recall receive
recipe record recycle reduce reflect reform refuse region regret regular
reject relax release relief rely remain remember remind remove render
renew rent reopen repair repeat replace report require rescue resemble
resist resource response result retire retreat return reunion reveal
review reward rhythm rib ribbon rice rich ride ridge rifle right rigid
ring riot ripple risk ritual rival river road roast robot robust rocket
romance roof rookie room rose rotate rough round route royal rubber rude
rug rule run runway rural sad saddle sadness safe sail salad salmon salon
salt salute same sample sand satisfy satoshi sauce sausage save say scale
scan scare scatter scene scheme school science scissors scorpion scout
scrap screen script scrub sea search season seat second secret section
security seed seek segment select sell seminar senior sense sentence series
service session settle setup seven shadow shaft shallow share shed shell
sheriff shield shift shine ship shiver shock shoe shoot shop short shoulder
shove shrimp shrug shuffle shy sibling sick side siege sight sign silent
silk silly silver similar simple since sing siren sister situate six size
skate sketch ski skill skin skirt skull slab slam sleep slender slice slide
slight slim slogan slot slow slush small smart smile smoke smooth snack
snake snap sniff snow soap soccer social sock soda soft solar soldier solid
solution solve someone song soon sorry sort soul sound soup source south
space spare spatial spawn speak special speed spell spend sphere spice
spider spike spin spirit split spoil sponsor spoon sport spot spray spread
spring spy square squeeze squirrel stable stadium staff stage stairs stamp
stand start state stay steak steel stem step stereo stick still sting stock
stomach stone stool story stove strategy street strike strong struggle
student stuff stumble style subject submit subway success such sudden
suffer sugar suggest suit summer sun sunny sunset super supply supreme
sure surface surge surprise surround survey suspect sustain swallow swamp
swap swarm swear sweet swift swim swing switch sword symbol symptom syrup
system table tackle tag tail talent talk tank tape target task taste tattoo
taxi teach team tell ten tenant tennis tent term test text thank that theme
then theory there they thing this thought three thrive throw thumb thunder
ticket tide tiger tilt timber time tiny tip tired tissue title toast
tobacco today toddler toe together toilet token tomato tomorrow tone tongue
tonight tool tooth top topic topple torch tornado tortoise toss total
tourist toward tower town toy track trade traffic tragic train transfer
trap trash travel tray treat tree trend trial tribe trick trigger trim trip
trophy trouble truck true truly trumpet trust truth try tube tuition tumble
tuna tunnel turkey turn turtle twelve twenty twice twin twist two type
typical ugly umbrella unable unaware uncle uncover under undo unfair unfold
unhappy uniform unique unit universe unknown unlock until unusual unveil
update upgrade uphold upon upper upset urban urge usage use used useful
useless usual utility vacant vacuum vague valid valley valve van vanish
vapor various vast vault vehicle velvet vendor venture venue verb verify
version very vessel veteran viable vibrant vicious victory video view
village vintage violin virtual virus visa visit visual vital vivid vocal
voice void volcano volume vote voyage wage wagon wait walk wall walnut want
warfare warm warrior wash wasp waste water wave way wealth weapon wear
weasel weather web wedding weekend weird welcome west wet whale what wheat
wheel when where whip whisper wide width wife wild will win window wine
wing wink winner winter wire wisdom wise wish witness wolf woman wonder
wood wool word work world worry worth wrap wreck wrestle wrist write wrong
yard year yellow you young youth zebra zero zone zoo
"""

WORDLIST = _WORDLIST_RAW.split()
assert len(WORDLIST) == 2048, "BIP-39 wordlist must contain exactly 2048 words"
WORD_INDEX = {w: i for i, w in enumerate(WORDLIST)}
assert len(WORD_INDEX) == 2048, "BIP-39 wordlist must contain no duplicates"

# Hash of the canonical file form: one word per line, trailing newline.
WORDLIST_SHA256 = hashlib.sha256(
    ("\n".join(WORDLIST) + "\n").encode("utf-8")).hexdigest()
OFFICIAL_WORDLIST_SHA256 = \
    "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"


# ===========================================================================
# Hash primitives the standard library does not provide
# ===========================================================================
def ripemd160(data):
    """RIPEMD-160.

    hashlib can usually provide this, but OpenSSL 3 moved RIPEMD-160 into the
    legacy provider, so on many current Python builds hashlib.new('ripemd160')
    raises.  Try it, and fall back to this implementation of the specification.
    """
    try:
        h = hashlib.new("ripemd160")
        h.update(data)
        return h.digest()
    except (ValueError, TypeError):
        return _ripemd160_py(data)


_R_RHO = [7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8]
_R_PI = [(9 * i + 5) % 16 for i in range(16)]
_R_SHIFTS = [
    [11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8],
    [12, 13, 11, 15, 6, 9, 9, 7, 12, 15, 11, 13, 7, 8, 7, 7],
    [13, 15, 14, 11, 7, 7, 6, 8, 13, 14, 13, 12, 5, 5, 6, 9],
    [14, 11, 12, 14, 8, 6, 5, 5, 15, 12, 15, 14, 9, 9, 8, 6],
    [15, 12, 13, 13, 9, 5, 8, 6, 14, 11, 12, 11, 8, 6, 5, 5],
]
_R_KL = [0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E]
_R_KR = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000]


def _r_rol(x, n):
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def _r_f(j, x, y, z):
    if j < 16:
        return x ^ y ^ z
    if j < 32:
        return (x & y) | (~x & z)
    if j < 48:
        return (x | ~y) ^ z
    if j < 64:
        return (x & z) | (y & ~z)
    return x ^ (y | ~z)


def _ripemd160_py(message):
    # Build the round index and shift schedules from the specification.
    idx_l = list(range(16))
    idx_r = list(_R_PI)
    for _ in range(4):
        idx_l += [_R_RHO[i] for i in idx_l[-16:]]
        idx_r += [_R_RHO[i] for i in idx_r[-16:]]
    shift_l = [_R_SHIFTS[j // 16][idx_l[j]] for j in range(80)]
    shift_r = [_R_SHIFTS[j // 16][idx_r[j]] for j in range(80)]

    h = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0]
    ml = len(message)
    message = message + b"\x80"
    message += b"\x00" * ((56 - len(message) % 64) % 64)
    message += (ml * 8).to_bytes(8, "little")

    for off in range(0, len(message), 64):
        block = message[off:off + 64]
        x = [int.from_bytes(block[i * 4:i * 4 + 4], "little") for i in range(16)]
        al, bl, cl, dl, el = h
        ar, br, cr, dr, er = h
        for j in range(80):
            t = (_r_rol((al + _r_f(j, bl, cl, dl) + x[idx_l[j]]
                         + _R_KL[j // 16]) & 0xFFFFFFFF, shift_l[j]) + el)
            al, bl, cl, dl, el = el, t & 0xFFFFFFFF, bl, _r_rol(cl, 10), dl
            t = (_r_rol((ar + _r_f(79 - j, br, cr, dr) + x[idx_r[j]]
                         + _R_KR[j // 16]) & 0xFFFFFFFF, shift_r[j]) + er)
            ar, br, cr, dr, er = er, t & 0xFFFFFFFF, br, _r_rol(cr, 10), dr
        h = [(h[1] + cl + dr) & 0xFFFFFFFF,
             (h[2] + dl + er) & 0xFFFFFFFF,
             (h[3] + el + ar) & 0xFFFFFFFF,
             (h[4] + al + br) & 0xFFFFFFFF,
             (h[0] + bl + cr) & 0xFFFFFFFF]
    return b"".join(v.to_bytes(4, "little") for v in h)


_KECCAK_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
    0x8000000080008000, 0x000000000000808B, 0x0000000080000001,
    0x8000000080008081, 0x8000000000008009, 0x000000000000008A,
    0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089,
    0x8000000000008003, 0x8000000000008002, 0x8000000000000080,
    0x000000000000800A, 0x800000008000000A, 0x8000000080008081,
    0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]
_KECCAK_ROT = [
    [0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61],
    [28, 55, 25, 21, 56], [27, 20, 39, 8, 14],
]


def keccak256(data):
    """Keccak-256 as used by Ethereum.

    This is NOT hashlib.sha3_256: NIST changed the padding byte from 0x01 to
    0x06 when standardising SHA-3, so the two produce different digests for
    the same input.  Ethereum uses the original Keccak padding.
    """
    rate = 136  # 1088 bits for a 256-bit digest
    a = [[0] * 5 for _ in range(5)]

    def keccak_f():
        for rnd in range(24):
            c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
            d = [c[(x - 1) % 5] ^ (((c[(x + 1) % 5] << 1)
                                    | (c[(x + 1) % 5] >> 63)) & 0xFFFFFFFFFFFFFFFF)
                 for x in range(5)]
            for x in range(5):
                for y in range(5):
                    a[x][y] ^= d[x]
            b = [[0] * 5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    r = _KECCAK_ROT[x][y]
                    v = a[x][y]
                    b[y][(2 * x + 3 * y) % 5] = (((v << r) | (v >> (64 - r)))
                                                 & 0xFFFFFFFFFFFFFFFF) if r else v
            for x in range(5):
                for y in range(5):
                    a[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y]
                                         & 0xFFFFFFFFFFFFFFFF)
            a[0][0] ^= _KECCAK_RC[rnd]

    padded = bytearray(data)
    padded.append(0x01)                       # original Keccak padding
    while len(padded) % rate != 0:
        padded.append(0x00)
    padded[-1] |= 0x80

    for off in range(0, len(padded), rate):
        block = padded[off:off + rate]
        for i in range(rate // 8):
            x, y = i % 5, i // 5
            a[x][y] ^= int.from_bytes(block[i * 8:i * 8 + 8], "little")
        keccak_f()

    out = b""
    for i in range(4):
        x, y = i % 5, i // 5
        out += a[x][y].to_bytes(8, "little")
    return out[:32]


def sha256d(b):
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()


def hash160(b):
    return ripemd160(hashlib.sha256(b).digest())


# ===========================================================================
# Base58 / Bech32
# ===========================================================================
B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(raw):
    n = int.from_bytes(raw, "big")
    out = ""
    while n > 0:
        n, r = divmod(n, 58)
        out = B58_ALPHABET[r] + out
    pad = len(raw) - len(raw.lstrip(b"\x00"))
    return "1" * pad + out


def b58decode(s):
    n = 0
    for ch in s:
        i = B58_ALPHABET.find(ch)
        if i < 0:
            raise ValueError("invalid base58 character %r" % ch)
        n = n * 58 + i
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + body


def b58check_encode(payload):
    return b58encode(payload + sha256d(payload)[:4])


BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
BECH32_CONST = 1
BECH32M_CONST = 0x2BC830A3


def _bech32_polymod(values):
    gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ v
        for i in range(5):
            chk ^= gen[i] if ((top >> i) & 1) else 0
    return chk


def _bech32_hrp_expand(hrp):
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def _convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            return None
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        return None
    return ret


def bech32_encode(hrp, witver, witprog):
    """Encode a SegWit address. Witness v0 uses Bech32, v1+ uses Bech32m."""
    data = [witver] + _convertbits(list(witprog), 8, 5)
    const = BECH32_CONST if witver == 0 else BECH32M_CONST
    values = _bech32_hrp_expand(hrp) + data
    polymod = _bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    checksum = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(BECH32_CHARSET[d] for d in data + checksum)


# ===========================================================================
# secp256k1  (Bitcoin, Ethereum, and the BIP-32 chain Mina derives through)
# ===========================================================================
SECP_P = 2 ** 256 - 2 ** 32 - 977
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECP_G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
          0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)


def _wei_add(p, q, prime, a=0):
    """Point addition on a short Weierstrass curve y^2 = x^3 + ax + b."""
    if p is None:
        return q
    if q is None:
        return p
    x1, y1 = p
    x2, y2 = q
    if x1 == x2 and (y1 + y2) % prime == 0:
        return None
    if p == q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, prime - 2, prime) % prime
    else:
        lam = (y2 - y1) * pow(x2 - x1, prime - 2, prime) % prime
    x3 = (lam * lam - x1 - x2) % prime
    return (x3, (lam * (x1 - x3) - y1) % prime)


def _jac_dbl(p, prime, a):
    x, y, z = p
    if z == 0 or y == 0:
        return (0, 0, 0)
    yy = y * y % prime
    s = 4 * x * yy % prime
    m = 3 * x * x % prime
    if a:
        m = (m + a * pow(z, 4, prime)) % prime
    x3 = (m * m - 2 * s) % prime
    return (x3, (m * (s - x3) - 8 * yy * yy) % prime, 2 * y * z % prime)


def _jac_add(p, q, prime, a):
    x1, y1, z1 = p
    x2, y2, z2 = q
    if z1 == 0:
        return q
    if z2 == 0:
        return p
    z1z1 = z1 * z1 % prime
    z2z2 = z2 * z2 % prime
    u1 = x1 * z2z2 % prime
    u2 = x2 * z1z1 % prime
    s1 = y1 * z2 % prime * z2z2 % prime
    s2 = y2 * z1 % prime * z1z1 % prime
    if u1 == u2:
        return _jac_dbl(p, prime, a) if s1 == s2 else (0, 0, 0)
    h = (u2 - u1) % prime
    r = (s2 - s1) % prime
    hh = h * h % prime
    hhh = h * hh % prime
    u1hh = u1 * hh % prime
    x3 = (r * r - hhh - 2 * u1hh) % prime
    return (x3, (r * (u1hh - x3) - s1 * hhh) % prime, h * z1 % prime * z2 % prime)


def _wei_mul(k, point, prime, a=0):
    """Scalar multiplication in Jacobian coordinates.

    Affine addition needs a modular inverse at every step, which made a full
    nine-chain derivation take about a second.  Jacobian coordinates defer all
    of them to a single inverse at the end.  Both curves used here, secp256k1
    and Pallas, have a = 0.
    """
    if k == 0 or point is None:
        return None
    acc = (0, 0, 0)
    addend = (point[0], point[1], 1)
    while k:
        if k & 1:
            acc = _jac_add(acc, addend, prime, a)
        addend = _jac_dbl(addend, prime, a)
        k >>= 1
    if acc[2] == 0:
        return None
    zi = pow(acc[2], prime - 2, prime)
    zi2 = zi * zi % prime
    return (acc[0] * zi2 % prime, acc[1] * zi2 % prime * zi % prime)


def secp_pubkey(priv_int):
    return _wei_mul(priv_int, SECP_G, SECP_P)


def ser_compressed(point):
    x, y = point
    return (b"\x03" if y & 1 else b"\x02") + x.to_bytes(32, "big")


def ser_uncompressed_xy(point):
    x, y = point
    return x.to_bytes(32, "big") + y.to_bytes(32, "big")


# ===========================================================================
# ed25519  (Solana, Aptos, Sui)
# ===========================================================================
ED_P = 2 ** 255 - 19
ED_L = 2 ** 252 + 27742317777372353535851937790883648493
ED_D = (-121665 * pow(121666, ED_P - 2, ED_P)) % ED_P
ED_I = pow(2, (ED_P - 1) // 4, ED_P)


def _ed_recover_x(y, sign):
    xx = (y * y - 1) * pow(ED_D * y * y + 1, ED_P - 2, ED_P) % ED_P
    x = pow(xx, (ED_P + 3) // 8, ED_P)
    if (x * x - xx) % ED_P != 0:
        x = x * ED_I % ED_P
    if x % 2 != sign:
        x = ED_P - x
    return x


_ED_BY = 4 * pow(5, ED_P - 2, ED_P) % ED_P
_ED_BX = _ed_recover_x(_ED_BY, 0)
ED_B = (_ED_BX, _ED_BY, 1, _ED_BX * _ED_BY % ED_P)


def _ed_add(p, q):
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % ED_P
    b = (y1 + x1) * (y2 + x2) % ED_P
    c = t1 * 2 * ED_D * t2 % ED_P
    d = z1 * 2 * z2 % ED_P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % ED_P, g * h % ED_P, f * g % ED_P, e * h % ED_P)


def _ed_mul(point, scalar):
    q = (0, 1, 1, 0)
    while scalar > 0:
        if scalar & 1:
            q = _ed_add(q, point)
        point = _ed_add(point, point)
        scalar >>= 1
    return q


def ed25519_pubkey(seed32):
    """RFC 8032 ed25519 public key from a 32-byte private seed."""
    h = hashlib.sha512(seed32).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8          # clear the low 3 bits
    a |= 1 << 254                # set bit 254
    x, y, z, _ = _ed_mul(ED_B, a)
    zi = pow(z, ED_P - 2, ED_P)
    x = x * zi % ED_P
    y = y * zi % ED_P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


# ===========================================================================
# Pallas curve  (Mina)
# ===========================================================================
# y^2 = x^3 + 5 over Fp.  Note the base point below is the one o1js and
# mina-signer use, which is NOT the (-1, 2) generator given in the Pasta
# curves specification -- using the spec generator produces wrong addresses.
PALLAS_P = 28948022309329048855892746252171976963363056481941560715954676764349967630337
PALLAS_Q = 28948022309329048855892746252171976963363056481941647379679742748393362948097
PALLAS_G = (1,
            12418654782883325593414442427049395787963493412651469444558597405572177144507)


def pallas_pubkey(scalar):
    return _wei_mul(scalar, PALLAS_G, PALLAS_P)


# ===========================================================================
# BIP-39
# ===========================================================================
VALID_WORD_COUNTS = (12, 15, 18, 21, 24)


def words_to_bits(word_count):
    """(entropy bits, checksum bits, total bits) for a mnemonic length."""
    if word_count not in VALID_WORD_COUNTS:
        raise ValueError("word count must be one of %s" % (VALID_WORD_COUNTS,))
    total = word_count * 11
    ent = total * 32 // 33
    return ent, total - ent, total


def entropy_to_mnemonic(entropy):
    """entropy bytes -> mnemonic word list, appending the SHA-256 checksum."""
    ent_bits = len(entropy) * 8
    if ent_bits not in (128, 160, 192, 224, 256):
        raise ValueError("entropy must be 128/160/192/224/256 bits, got %d"
                         % ent_bits)
    cs_bits = ent_bits // 32
    checksum = hashlib.sha256(entropy).digest()
    bits = (int.from_bytes(entropy, "big") << cs_bits) | (checksum[0] >> (8 - cs_bits))
    total = ent_bits + cs_bits
    return [WORDLIST[(bits >> (total - 11 * (i + 1))) & 0x7FF]
            for i in range(total // 11)]


def mnemonic_to_entropy(words):
    """Reverse of entropy_to_mnemonic. Raises ValueError on a bad checksum."""
    if len(words) not in VALID_WORD_COUNTS:
        raise ValueError("mnemonic must be %s words, got %d"
                         % ("/".join(map(str, VALID_WORD_COUNTS)), len(words)))
    bits = 0
    for w in words:
        if w not in WORD_INDEX:
            raise ValueError("'%s' is not in the BIP-39 wordlist" % w)
        bits = (bits << 11) | WORD_INDEX[w]
    ent_bits, cs_bits, total = words_to_bits(len(words))
    entropy = (bits >> cs_bits).to_bytes(ent_bits // 8, "big")
    want = hashlib.sha256(entropy).digest()[0] >> (8 - cs_bits)
    got = bits & ((1 << cs_bits) - 1)
    if want != got:
        raise ValueError("checksum mismatch: phrase carries %s but the entropy "
                         "requires %s (a word is wrong or out of order)"
                         % (format(got, "0%db" % cs_bits),
                            format(want, "0%db" % cs_bits)))
    return entropy


def checksum_bits_of(entropy):
    cs_bits = len(entropy) * 8 // 32
    return hashlib.sha256(entropy).digest()[0] >> (8 - cs_bits), cs_bits


def mnemonic_to_seed(words, passphrase=""):
    """BIP-39 seed: PBKDF2-HMAC-SHA512, 2048 rounds, salt 'mnemonic'+passphrase."""
    mnemonic = unicodedata.normalize("NFKD", " ".join(words))
    salt = unicodedata.normalize("NFKD", "mnemonic" + passphrase)
    return hashlib.pbkdf2_hmac("sha512", mnemonic.encode("utf-8"),
                               salt.encode("utf-8"), 2048, 64)


# ===========================================================================
# BIP-32 (secp256k1) and SLIP-10 (ed25519) derivation
# ===========================================================================
H = 0x80000000   # hardened offset


def parse_path(path):
    parts = path.strip().split("/")
    if parts[0] not in ("m", "M"):
        raise ValueError("derivation path must start with m/")
    out = []
    for p in parts[1:]:
        if not p:
            continue
        hardened = p[-1] in ("'", "h", "H")
        n = int(p[:-1] if hardened else p)
        out.append(n + H if hardened else n)
    return out


def bip32_master(seed):
    i = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    return int.from_bytes(i[:32], "big"), i[32:]


def bip32_ckd(key, chain, index):
    if index >= H:
        data = b"\x00" + key.to_bytes(32, "big") + index.to_bytes(4, "big")
    else:
        data = ser_compressed(secp_pubkey(key)) + index.to_bytes(4, "big")
    i = hmac.new(chain, data, hashlib.sha512).digest()
    child = (int.from_bytes(i[:32], "big") + key) % SECP_N
    if int.from_bytes(i[:32], "big") >= SECP_N or child == 0:
        raise ValueError("invalid child key; use the next index")
    return child, i[32:]


def bip32_derive(seed, path):
    key, chain = bip32_master(seed)
    for index in parse_path(path):
        key, chain = bip32_ckd(key, chain, index)
    return key, chain


def slip10_ed25519_derive(seed, path):
    """SLIP-0010 ed25519. Every step is hardened; unhardened is undefined."""
    i = hmac.new(b"ed25519 seed", seed, hashlib.sha512).digest()
    key, chain = i[:32], i[32:]
    for index in parse_path(path):
        if index < H:
            index += H     # ed25519 supports hardened derivation only
        data = b"\x00" + key + index.to_bytes(4, "big")
        i = hmac.new(chain, data, hashlib.sha512).digest()
        key, chain = i[:32], i[32:]
    return key, chain


# ===========================================================================
# Address encodings
# ===========================================================================
def btc_p2pkh(pubkey):
    return b58check_encode(b"\x00" + hash160(pubkey))


def btc_p2sh_p2wpkh(pubkey):
    redeem = b"\x00\x14" + hash160(pubkey)
    return b58check_encode(b"\x05" + hash160(redeem))


def btc_p2wpkh(pubkey):
    return bech32_encode("bc", 0, hash160(pubkey))


def _tagged_hash(tag, msg):
    t = hashlib.sha256(tag.encode()).digest()
    return hashlib.sha256(t + t + msg).digest()


def btc_p2tr(pubkey_point):
    """BIP-86 Taproot: tweak the internal key by t = H_TapTweak(x) and encode
    the x-only result as a witness v1 program (Bech32m)."""
    x, y = pubkey_point
    if y & 1:                       # lift_x: use the even-y point
        y = SECP_P - y
    xbytes = x.to_bytes(32, "big")
    t = int.from_bytes(_tagged_hash("TapTweak", xbytes), "big")
    if t >= SECP_N:
        raise ValueError("invalid taproot tweak")
    q = _wei_add((x, y), _wei_mul(t, SECP_G, SECP_P), SECP_P)
    return bech32_encode("bc", 1, q[0].to_bytes(32, "big"))


def eth_address(pubkey_point):
    """EIP-55 checksummed Ethereum address."""
    digest = keccak256(ser_uncompressed_xy(pubkey_point))
    body = digest[-20:].hex()
    h = keccak256(body.encode("ascii")).hex()
    return "0x" + "".join(c.upper() if c.isalpha() and int(h[i], 16) >= 8 else c
                          for i, c in enumerate(body))


def wif(priv_int, compressed=True):
    payload = b"\x80" + priv_int.to_bytes(32, "big") + (b"\x01" if compressed else b"")
    return b58check_encode(payload)


def solana_address(pubkey32):
    return b58encode(pubkey32)


def aptos_address(pubkey32):
    return "0x" + hashlib.sha3_256(pubkey32 + b"\x00").hexdigest()


def sui_address(pubkey32):
    return "0x" + hashlib.blake2b(b"\x00" + pubkey32, digest_size=32).hexdigest()


def mina_address(point):
    x, y = point
    body = bytes([0xCB, 0x01, 0x01]) + x.to_bytes(32, "little") + bytes([y & 1])
    return b58encode(body + sha256d(body)[:4])


def mina_private_key_b58(scalar_le_bytes):
    return b58check_encode(bytes([0x5A, 0x01]) + scalar_le_bytes)


# ===========================================================================
# The derivation table
# ===========================================================================
# (key, label, path template, curve)  -- curve is 'secp', 'ed25519' or 'mina'.
# {a} is the account index; every wallet named in the UI uses account 0 by
# default, which is what these templates produce.
DERIVATIONS = [
    ("btc44", "Bitcoin  Legacy  P2PKH", "m/44'/0'/{a}'/0/0", "secp"),
    ("btc49", "Bitcoin  Nested SegWit  P2SH-P2WPKH", "m/49'/0'/{a}'/0/0", "secp"),
    ("btc84", "Bitcoin  Native SegWit  P2WPKH", "m/84'/0'/{a}'/0/0", "secp"),
    ("btc86", "Bitcoin  Taproot  P2TR", "m/86'/0'/{a}'/0/0", "secp"),
    ("eth", "Ethereum  (+ EVM chains)", "m/44'/60'/{a}'/0/0", "secp"),
    ("mina", "Mina  Pallas curve", "m/44'/12586'/{a}'/0/0", "mina"),
    ("sol", "Solana", "m/44'/501'/{a}'/0'", "ed25519"),
    ("apt", "Aptos", "m/44'/637'/{a}'/0'/0'", "ed25519"),
    ("sui", "Sui", "m/44'/784'/{a}'/0'/0'", "ed25519"),
]


def derive_all(seed, account=0):
    """Derive every supported chain from a BIP-39 seed.

    Returns an ordered list of dicts with the path, private key, public key
    and address for each entry in DERIVATIONS.
    """
    out = []
    for key, label, template, curve in DERIVATIONS:
        path = template.format(a=account)
        rec = {"key": key, "label": label, "path": path, "curve": curve}
        if curve == "secp":
            priv, _ = bip32_derive(seed, path)
            point = secp_pubkey(priv)
            rec["priv_hex"] = "%064x" % priv
            rec["pub_hex"] = ser_compressed(point).hex()
            if key == "btc44":
                rec["priv_disp"] = wif(priv)
                rec["addr"] = btc_p2pkh(ser_compressed(point))
            elif key == "btc49":
                rec["priv_disp"] = wif(priv)
                rec["addr"] = btc_p2sh_p2wpkh(ser_compressed(point))
            elif key == "btc84":
                rec["priv_disp"] = wif(priv)
                rec["addr"] = btc_p2wpkh(ser_compressed(point))
            elif key == "btc86":
                rec["priv_disp"] = wif(priv)
                rec["addr"] = btc_p2tr(point)
            elif key == "eth":
                rec["priv_disp"] = "0x" + rec["priv_hex"]
                rec["pub_hex"] = "0x04" + ser_uncompressed_xy(point).hex()
                rec["addr"] = eth_address(point)
        elif curve == "ed25519":
            k, _ = slip10_ed25519_derive(seed, path)
            pub = ed25519_pubkey(k)
            rec["priv_hex"] = k.hex()
            rec["pub_hex"] = pub.hex()
            if key == "sol":
                # Solana wallets show the 64-byte keypair in base58
                rec["priv_disp"] = b58encode(k + pub)
                rec["addr"] = solana_address(pub)
            elif key == "apt":
                rec["priv_disp"] = "0x" + k.hex()
                rec["addr"] = aptos_address(pub)
            else:
                rec["priv_disp"] = "0x" + k.hex()
                rec["addr"] = sui_address(pub)
        else:  # mina
            priv, _ = bip32_derive(seed, path)
            raw = bytearray(priv.to_bytes(32, "big"))
            raw[0] &= 0x3F                       # clamp into the Pallas scalar field
            scalar = int.from_bytes(bytes(raw), "big")
            point = pallas_pubkey(scalar)
            rec["priv_hex"] = bytes(raw).hex()
            rec["priv_disp"] = mina_private_key_b58(bytes(raw)[::-1])
            rec["pub_hex"] = "%064x" % point[0]
            rec["addr"] = mina_address(point)
        out.append(rec)
    return out


# speed slider 1..10  ->  (frames per cell, ms per frame)
SPEED_TABLE = {
    1: (16, 55), 2: (14, 45), 3: (12, 38), 4: (10, 32), 5: (8, 28),
    6: (6, 24), 7: (5, 18), 8: (4, 14), 9: (3, 10), 10: (2, 8),
}


# ----------------------------------------------------------------------------
# Scrollable container

class SimTab(ttk.Frame):
    ROUNDS = 1
    PER_ROUND = 1
    NOUN = "toss"
    NOUN_PL = "tosses"
    RESET_LABEL = "Retoss"
    DEFAULT_SPEED = 7

    def __init__(self, parent, app):
        super().__init__(parent, style="Bg.TFrame")
        self.app = app
        self.N = self.ROUNDS * self.PER_ROUND
        self.results = [None] * self.N
        self.cursor = 0
        self.playing = False
        self.single_shot = False
        self._after = None

        self.target = None
        self.pending_value = None
        self.last_value = None
        self.f_total = 1
        self.f_left = 0
        self.frame_ms = 20

        self.mode_var = tk.StringVar(value=MODE_OS_SEED)
        self.seed_var = tk.StringVar(value="")
        self.speed_var = tk.IntVar(value=self.DEFAULT_SPEED)
        self.status_var = tk.StringVar(value="")
        self.engine_var = tk.StringVar(value="")

        self.engine = None
        self.run_started = None

        self.scroll = Scrollable(self)
        self.scroll.pack(fill="both", expand=True)
        self.body = self.scroll.inner

        self._build_controls(self.body)
        self._build_body(self.body)
        self.new_engine()
        self.reset(initial=True)

    # -- engine -------------------------------------------------------------
    def new_engine(self):
        self.engine = Engine(self.mode_var.get(), self.seed_var.get())
        self.run_started = datetime.now()
        rep = "reproducible" if self.engine.reproducible else "not reproducible"
        self.engine_var.set("key fingerprint  %s        %s"
                            % (self.engine.fingerprint, rep))

    def on_source_change(self, *_a):
        self.stop()
        self.new_engine()
        self.reset()
        self.note_var.set(MODE_NOTE.get(self.mode_var.get(), ""))

    # -- controls -----------------------------------------------------------
    def _build_controls(self, parent):
        bar = ttk.Frame(parent, style="Card.TFrame", padding=(14, 11))
        bar.pack(fill="x", padx=12, pady=(12, 8))

        ttk.Label(bar, text="Source", style="Key.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        cb = ttk.Combobox(bar, textvariable=self.mode_var, values=MODES,
                          state="readonly", width=44, style="Dark.TCombobox")
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", self.on_source_change)

        ttk.Label(bar, text="Initial seed", style="Key.TLabel").grid(
            row=0, column=2, sticky="w", padx=(20, 8))
        se = ttk.Entry(bar, textvariable=self.seed_var, width=26, style="Dark.TEntry")
        se.grid(row=0, column=3, sticky="w")
        se.bind("<Return>", self.on_source_change)
        se.bind("<FocusOut>", lambda e: None)
        ttk.Button(bar, text="Apply seed", style="Ghost.TButton",
                   command=self.on_source_change).grid(row=0, column=4, padx=(8, 0))

        ttk.Label(bar, text="Speed", style="Key.TLabel").grid(
            row=0, column=5, sticky="e", padx=(22, 8))
        sc = ttk.Scale(bar, from_=1, to=10, orient="horizontal", length=130,
                       command=lambda v: self.speed_var.set(int(round(float(v)))))
        sc.set(self.DEFAULT_SPEED)
        sc.grid(row=0, column=6, sticky="w")

        btns = ttk.Frame(bar, style="Card.TFrame")
        btns.grid(row=1, column=0, columnspan=7, sticky="w", pady=(12, 0))
        self.play_btn = ttk.Button(btns, text="▶  Play", style="Accent.TButton",
                                   command=self.play)
        self.play_btn.pack(side="left")
        self.pause_btn = ttk.Button(btns, text="▮▮  Pause", style="Ghost.TButton",
                                    command=self.pause, state="disabled")
        self.pause_btn.pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="⇥  Fill rest", style="Ghost.TButton",
                   command=self.fill_rest).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="↻  " + self.RESET_LABEL, style="Ghost.TButton",
                   command=self.reset).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="Copy values", style="Ghost.TButton",
                   command=self.copy_values).pack(side="left", padx=(24, 0))
        ttk.Button(btns, text="Save run", style="Ghost.TButton",
                   command=self.save_run).pack(side="left", padx=(8, 0))

        self.note_var = tk.StringVar(value=MODE_NOTE[MODE_OS_SEED])
        ttk.Label(bar, textvariable=self.note_var, style="Note.TLabel",
                  wraplength=1120, justify="left").grid(
            row=2, column=0, columnspan=7, sticky="w", pady=(11, 0))
        ttk.Label(bar, textvariable=self.engine_var, style="Mono2.TLabel").grid(
            row=3, column=0, columnspan=7, sticky="w", pady=(5, 0))

    # -- subclass hooks -----------------------------------------------------
    def _build_body(self, parent):
        raise NotImplementedError

    def _new_value(self):
        raise NotImplementedError

    def _paint_cell(self, idx):
        raise NotImplementedError

    def _draw_stage(self, t=None, value=None):
        raise NotImplementedError

    def _refresh_values(self):
        raise NotImplementedError

    def _refresh_stats(self):
        raise NotImplementedError

    def _run_report(self):
        raise NotImplementedError

    # -- playback -----------------------------------------------------------
    def _cancel(self):
        if self._after is not None:
            try:
                self.after_cancel(self._after)
            except Exception:
                pass
            self._after = None

    def stop(self):
        self._cancel()
        self.playing = False
        self.single_shot = False
        self.target = None
        self.pending_value = None
        self._sync_buttons()

    def _speed(self):
        s = max(1, min(10, int(self.speed_var.get())))
        return SPEED_TABLE[s]

    def _first_blank(self):
        for i in range(self.N):
            if self.results[i] is None:
                return i
        return None

    def _sync_buttons(self):
        done = self._first_blank() is None
        self.play_btn.configure(
            state=("disabled" if (self.playing or done) else "normal"),
            text="▶  Play" if self.cursor == 0 else "▶  Resume")
        self.pause_btn.configure(state=("normal" if self.playing else "disabled"))

    def play(self):
        if self.playing:
            return
        if self.cursor >= self.N:
            # Parked at the end. Jump to the first still-blank cell, if any,
            # so Play always has something to do (e.g. after a shift+click
            # run that started part-way down the grid).
            nxt = self._first_blank()
            if nxt is None:
                return
            self.cursor = nxt
        self.playing = True
        self.single_shot = False
        self._sync_buttons()
        self._tick()

    def pause(self):
        if not self.playing:
            return
        self._cancel()
        self.playing = False
        # Keep target and pending_value. The value for the in-flight cell was
        # already drawn from the source; discarding it here would silently
        # waste entropy and desynchronise the byte counter. Resume replays the
        # animation for that same, already-decided value.
        self.f_left = self.f_total
        self._draw_stage()
        self._sync_buttons()
        self._set_status()

    def _commit_pending(self):
        """Commit an in-flight value (drawn but not yet shown) if there is one."""
        if self.target is not None and self.pending_value is not None:
            idx = self.target
            self.results[idx] = self.pending_value
            self.last_value = self.pending_value
            self._paint_cell(idx)
            if idx >= self.cursor:
                self.cursor = idx + 1
        self.target = None
        self.pending_value = None

    def retoss_cell(self, idx):
        """Single click on a cell: re-toss ONLY that one. The play cursor is
        deliberately left where it is."""
        if self.playing:
            return
        self._commit_pending()
        self.target = idx
        self.pending_value = self._new_value()
        f, self.frame_ms = self._speed()
        self.f_total = max(f, 6)
        self.f_left = self.f_total
        self.playing = True
        self.single_shot = True
        self._sync_buttons()
        self._tick()

    def play_from(self, idx):
        """Shift+click on a cell: move the cursor there and play onward."""
        if self.playing:
            self.pause()
        self._commit_pending()
        self.cursor = idx
        self.play()

    def fill_rest(self):
        """Fill every still-blank cell instantly, no animation."""
        self._cancel()
        self.playing = False
        self.single_shot = False
        self._commit_pending()
        for i in range(self.N):
            if self.results[i] is None:
                self.results[i] = self._new_value()
                self.last_value = self.results[i]
                self._paint_cell(i)
        self.cursor = self.N
        self._draw_stage()
        self._refresh_values()
        self._refresh_stats()
        self._set_status()
        self._sync_buttons()

    def reset(self, initial=False):
        self.stop()
        self.results = [None] * self.N
        self.cursor = 0
        self.last_value = None
        if not initial:
            self.new_engine()
        for i in range(self.N):
            self._paint_cell(i)
        self._draw_stage()
        self._refresh_values()
        self._refresh_stats()
        self._set_status()
        self._sync_buttons()

    def _tick(self):
        self._after = None
        if not self.playing:
            return

        if self.target is None:
            if self.cursor >= self.N:
                self.playing = False
                self._draw_stage()
                self._set_status()
                self._sync_buttons()
                return
            self.target = self.cursor
            # The value is decided BEFORE the animation. The animation is a
            # readout of an already-drawn result, never the thing that
            # produces it.
            self.pending_value = self._new_value()
            self.f_total, self.frame_ms = self._speed()
            self.f_left = self.f_total

        self.f_left -= 1
        t = (self.f_total - self.f_left) / float(self.f_total)
        self._draw_stage(t=t, value=self.pending_value)

        if self.f_left <= 0:
            idx = self.target
            self.results[idx] = self.pending_value
            self.last_value = self.pending_value
            self._paint_cell(idx)
            self.target = None
            self.pending_value = None
            if self.single_shot:
                self.playing = False
                self.single_shot = False
                self._draw_stage()
                self._refresh_values()
                self._refresh_stats()
                self._set_status()
                self._sync_buttons()
                return
            self.cursor = idx + 1
            self._refresh_values()
            self._refresh_stats()
            self._set_status()

        self._after = self.after(self.frame_ms, self._tick)

    def _set_status(self):
        n = sum(1 for r in self.results if r is not None)
        if n == 0:
            self.status_var.set("stopped  -  press Play")
        elif n == self.N:
            self.status_var.set("complete  -  %d %s  -  press %s for a new draw"
                                % (self.N, self.NOUN_PL, self.RESET_LABEL))
        else:
            c = min(self.cursor, self.N - 1)
            rnd = c // self.PER_ROUND + 1
            pos = c % self.PER_ROUND + 1
            self.status_var.set("%d / %d %s   -   round %d, %s %d"
                                % (n, self.N, self.NOUN_PL, rnd, self.NOUN, pos))

    # -- output -------------------------------------------------------------
    def _set_text(self, widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        # Grow the box to its content so nothing is silently clipped - the tab
        # itself scrolls, so there is no reason to hide any of the draw.
        widget.configure(height=max(6, min(48, content.count("\n") + 1)),
                         state="disabled")

    def copy_values(self):
        txt = self.values_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(txt)
        self.app.flash("Values copied to clipboard.")

    def save_run(self):
        try:
            base = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base = os.getcwd()
        folder = os.path.join(base, "runs")
        os.makedirs(folder, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(folder, "%s_%s.txt" % (self.NOUN, stamp))
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._run_report())
        except OSError as exc:
            messagebox.showerror(APP_TITLE, "Could not save:\n%s" % exc)
            return
        self.app.flash("Saved  ->  runs\\%s" % os.path.basename(path))

    def _report_header(self):
        n = sum(1 for r in self.results if r is not None)
        return (
            "%s %s  -  %s run\n"
            "%s\n"
            "generated      %s\n"
            "source         %s\n"
            "seed           %s\n"
            "key finger     %s\n"
            "reproducible   %s\n"
            "completed      %d / %d %s\n"
            "bytes drawn    %d\n"
            % (APP_TITLE, APP_VER, self.NOUN,
               "=" * 74,
               datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               self.mode_var.get(),
               repr(self.seed_var.get()),
               self.engine.fingerprint,
               "yes" if self.engine.reproducible else "no",
               n, self.N, self.NOUN_PL,
               self.engine.bytes_drawn)
        )


# ----------------------------------------------------------------------------
# Statistics table widget

class CoinTab(SimTab):
    ROUNDS = 4
    PER_ROUND = 64
    NOUN = "toss"
    NOUN_PL = "tosses"
    RESET_LABEL = "Retoss"
    DEFAULT_SPEED = 7

    CELL = 23
    GAP = 3
    COLS = 8

    SPACE_ROUND = 2 ** 64
    SPACE_TOTAL = 2 ** 256

    def _build_body(self, parent):
        main = ttk.Frame(parent, style="Bg.TFrame")
        main.pack(fill="x", padx=12)

        # --- left: animated coin ------------------------------------------
        left = ttk.Frame(main, style="Card.TFrame", padding=(14, 12))
        left.pack(side="left", fill="y")
        ttk.Label(left, text="COIN", style="H2.TLabel").pack(anchor="w")
        ttk.Label(left, text="1 raw bit per toss  -  unbiased by construction",
                  style="Note.TLabel", wraplength=230, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.stage = tk.Canvas(left, width=232, height=232, bg=CARD,
                               highlightthickness=0, bd=0)
        self.stage.pack()
        self.face_var = tk.StringVar(value="")
        ttk.Label(left, textvariable=self.face_var, style="Face.TLabel").pack(
            pady=(6, 0))
        ttk.Label(left, textvariable=self.status_var, style="Note.TLabel",
                  wraplength=230, justify="left").pack(anchor="w", pady=(8, 0))
        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(left, text="OUTCOME SPACE", style="Key.TLabel").pack(anchor="w")
        ttk.Label(left, text="per round   2^64", style="Mono.TLabel").pack(anchor="w")
        ttk.Label(left, text=grouped(self.SPACE_ROUND), style="Mono2.TLabel",
                  wraplength=230, justify="left").pack(anchor="w")
        ttk.Label(left, text="4 rounds   (2^64)^4 = 2^256", style="Mono.TLabel").pack(
            anchor="w", pady=(6, 0))
        ttk.Label(left, text=sci(self.SPACE_TOTAL), style="Big.TLabel").pack(anchor="w")

        # --- right: the 4 x 64 grid ---------------------------------------
        right = ttk.Frame(main, style="Bg.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        grid = ttk.Frame(right, style="Bg.TFrame")
        grid.pack(anchor="nw")

        w = self.COLS * (self.CELL + self.GAP) + self.GAP
        self.blocks = []
        self.round_val = []
        for r in range(self.ROUNDS):
            blk = ttk.Frame(grid, style="Card.TFrame", padding=(10, 9))
            blk.grid(row=0, column=r, sticky="n", padx=(0 if r == 0 else 9, 0))
            ttk.Label(blk, text="ROUND %d" % (r + 1), style="H3.TLabel").pack(anchor="w")
            ttk.Label(blk, text="64 tosses  -  2^64", style="Note.TLabel").pack(
                anchor="w", pady=(0, 7))
            cv = tk.Canvas(blk, width=w, height=w, bg=CARD,
                           highlightthickness=0, bd=0, cursor="hand2")
            cv.pack()
            cv.bind("<Button-1>", lambda e, rr=r: self._cell_click(e, rr, False))
            cv.bind("<Shift-Button-1>", lambda e, rr=r: self._cell_click(e, rr, True))
            self.blocks.append(cv)
            v = tk.StringVar(value="-")
            ttk.Label(blk, textvariable=v, style="Mono2.TLabel",
                      wraplength=w, justify="left").pack(anchor="w", pady=(7, 0))
            self.round_val.append(v)

        # --- values panel --------------------------------------------------
        vp = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        vp.pack(fill="x", padx=12, pady=(10, 0))
        ttk.Label(vp, text="THE DRAW", style="H2.TLabel").pack(anchor="w")
        ttk.Label(vp, text="The 256 tosses read as one 256-bit integer. That single "
                           "number is the outcome, drawn from a space of 2^256.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.values_text = tk.Text(vp, height=15, bg=PANEL, fg=TEXT, bd=0,
                                   highlightthickness=1, highlightbackground=EDGE,
                                   highlightcolor=EDGE, insertbackground=TEXT,
                                   wrap="word", padx=12, pady=10,
                                   font=(MONO, 9))
        self.values_text.pack(fill="x")
        self.values_text.configure(state="disabled")

        # --- stats ----------------------------------------------------------
        sp = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        sp.pack(fill="x", padx=12, pady=(10, 14))
        ttk.Label(sp, text="RANDOMNESS QUALITY", style="H2.TLabel").pack(anchor="w")
        ttk.Label(sp, text="Measured on the tosses committed so far. Rows carrying a "
                           "p-value are hypothesis tests and are what the "
                           "pass / marginal / FAIL verdict refers to; balance and "
                           "entropy are descriptive only. With a single 256-toss "
                           "sample roughly 1 test in 100 reads 'marginal' purely by "
                           "chance - that is what a fair coin looks like, not "
                           "evidence of a fault.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.stats = StatsTable(sp, [
            ("counts", "Balance"),
            ("longest", "Longest run"),
            ("runs", "Runs test (Wald-Wolfowitz)"),
            ("chi", "Chi-square, uniform  df=1"),
            ("serial", "Serial pair test  df=3"),
            ("entropy", "Shannon entropy"),
            ("bytes", "Source consumption"),
        ])
        self.stats.pack(fill="x")

    # -- cells ---------------------------------------------------------------
    def _cell_click(self, event, rnd, shift):
        cv = self.blocks[rnd]
        step = self.CELL + self.GAP
        col = int((cv.canvasx(event.x) - self.GAP) // step)
        row = int((cv.canvasy(event.y) - self.GAP) // step)
        if not (0 <= col < self.COLS and 0 <= row < self.COLS):
            return
        idx = rnd * self.PER_ROUND + row * self.COLS + col
        if shift:
            self.play_from(idx)
        else:
            self.retoss_cell(idx)

    def _paint_cell(self, idx):
        rnd, k = divmod(idx, self.PER_ROUND)
        row, col = divmod(k, self.COLS)
        cv = self.blocks[rnd]
        tag = "c%d" % k
        cv.delete(tag)
        step = self.CELL + self.GAP
        x0 = self.GAP + col * step
        y0 = self.GAP + row * step
        x1, y1 = x0 + self.CELL, y0 + self.CELL
        v = self.results[idx]
        if v is None:
            rounded_rect(cv, x0, y0, x1, y1, 6, fill=PANEL, outline=EDGE,
                         width=1, tags=tag)
            cv.create_text((x0 + x1) / 2, (y0 + y1) / 2, text="·",
                           fill=DIM, font=(UI, 10), tags=tag)
        else:
            col_ = UP_C if v == 1 else DOWN_C
            rounded_rect(cv, x0, y0, x1, y1, 6, fill=col_, outline="", tags=tag)
            cv.create_text((x0 + x1) / 2, (y0 + y1) / 2 + 1,
                           text="↑" if v == 1 else "↓",
                           fill="#12151c", font=(UI, 11, "bold"), tags=tag)

    def _new_value(self):
        return self.engine.bit()

    # -- animated coin -------------------------------------------------------
    def _draw_stage(self, t=None, value=None):
        cv = self.stage
        cv.delete("all")
        w = 232
        cx, cy = w / 2.0, w / 2.0
        rad = 74.0

        if t is None:
            v = self.last_value
            theta = 0.0 if (v is None or v == 1) else math.pi
            lift = 0.0
            settled = True
            face_v = 1 if v is None else v
            idle = v is None
        else:
            # 3 full end-over-end turns, easing out, landing exactly on the
            # face that was already decided.
            total = 6.0 * math.pi + (0.0 if value == 1 else math.pi)
            theta = total * ease_out(t)
            lift = -math.sin(math.pi * t) * 30.0
            settled = t >= 1.0
            face_v = value
            idle = False

        c = math.cos(theta)
        ry = max(2.0, rad * abs(c))
        face = 1 if c >= 0 else 0
        if settled:
            face = face_v
            ry = rad
        yc = cy + lift

        # shadow
        sh = 1.0 - min(1.0, abs(lift) / 34.0)
        cv.create_oval(cx - rad * 0.72 * sh, cy + 84 - 7 * sh,
                       cx + rad * 0.72 * sh, cy + 84 + 7 * sh,
                       fill="#0a0d12", outline="")

        body = UP_C if face == 1 else DOWN_C
        if idle:
            body = PANEL
        rim = "#8a6410" if face == 1 else "#245e85"
        if idle:
            rim = EDGE

        # coin edge thickness
        cv.create_oval(cx - rad, yc - ry + 5, cx + rad, yc + ry + 5,
                       fill=rim, outline="")
        cv.create_oval(cx - rad, yc - ry, cx + rad, yc + ry,
                       fill=body, outline=rim, width=2)
        if ry > rad * 0.30:
            cv.create_oval(cx - rad * 0.80, yc - ry * 0.80,
                           cx + rad * 0.80, yc + ry * 0.80,
                           outline="#12151c", width=1)
            if idle:
                cv.create_text(cx, yc, text="?", fill=DIM, font=(UI, 34, "bold"))
            else:
                sz = max(10, int(30 * (ry / rad)))
                cv.create_text(cx, yc + 1,
                               text="↑" if face == 1 else "↓",
                               fill="#12151c", font=(UI, sz, "bold"))

        if idle:
            self.face_var.set("")
        else:
            self.face_var.set("UP" if face == 1 else "DOWN")

    # -- values --------------------------------------------------------------
    def _bits_of(self, rnd):
        lo = rnd * self.PER_ROUND
        return self.results[lo:lo + self.PER_ROUND]

    def _refresh_values(self):
        lines = []
        full_bits = []
        complete_rounds = 0
        for r in range(self.ROUNDS):
            bits = self._bits_of(r)
            s = "".join("1" if b == 1 else ("0" if b == 0 else "·") for b in bits)
            done = all(b is not None for b in bits)
            if done:
                complete_rounds += 1
                val = int(s, 2)
                self.round_val[r].set("0x%016X" % val)
                lines.append("ROUND %d   %s" % (r + 1, s[:32]))
                lines.append("          %s" % s[32:])
                lines.append("          hex 0x%016X" % val)
                lines.append("          int %s   of 2^64 = %s"
                             % (grouped(val), grouped(self.SPACE_ROUND)))
            else:
                n = sum(1 for b in bits if b is not None)
                self.round_val[r].set("%d / 64" % n)
                lines.append("ROUND %d   %s" % (r + 1, s[:32]))
                lines.append("          %s" % s[32:])
                lines.append("          incomplete  (%d / 64)" % n)
            lines.append("")
            full_bits.extend(bits)

        lines.append("-" * 88)
        if complete_rounds == self.ROUNDS:
            s = "".join(str(b) for b in full_bits)
            val = int(s, 2)
            hx = "%064X" % val
            lines.append("FULL 256-BIT DRAW")
            lines.append("  hex   " + " ".join(hx[i:i + 8] for i in range(0, 64, 8)))
            lines.append("  int   %s" % grouped(val))
            lines.append("")
            lines.append("  space 2^256 = %s" % grouped(self.SPACE_TOTAL))
            lines.append("              = %s" % sci(self.SPACE_TOTAL))
            lines.append("        this draw is 1 of those %s possibilities;"
                         % sci(self.SPACE_TOTAL, 5))
            lines.append("        the chance of repeating it is 1 in %s."
                         % sci(self.SPACE_TOTAL, 5))
        else:
            n = sum(1 for b in self.results if b is not None)
            lines.append("FULL 256-BIT DRAW      incomplete  (%d / 256 tosses)" % n)
            lines.append("")
            lines.append("  space 2^256 = %s" % grouped(self.SPACE_TOTAL))
            lines.append("              = %s" % sci(self.SPACE_TOTAL))
        self._set_text(self.values_text, "\n".join(lines))

    # -- statistics ----------------------------------------------------------
    def _refresh_stats(self):
        bits = [b for b in self.results if b is not None]
        n = len(bits)
        st = self.stats
        if n < 2:
            for k in ("counts", "longest", "runs", "chi", "serial", "entropy"):
                st.set(k, "-", MUTED)
            st.set("bytes", "%d bytes drawn from source" % self.engine.bytes_drawn, MUTED)
            return

        n1 = sum(bits)
        n0 = n - n1
        st.set("counts", "%d UP / %d DOWN     %.2f%% / %.2f%%     deviation %+d "
                         "from %.1f" % (n1, n0, 100.0 * n1 / n, 100.0 * n0 / n,
                                        n1 - n / 2.0, n / 2.0))

        lr = longest_run(bits)
        occ = expected_run_occurrences(n, lr, 2)
        c = GOOD if occ >= 0.05 else (WARN if occ >= 0.005 else BAD)
        st.set("longest", "%d identical in a row     typical longest ~%.1f for "
                          "n=%d     expected occurrences of a run this long: "
                          "%.3f" % (lr, math.log2(n), n, occ), c)

        rt = runs_test(bits)
        if rt:
            r, mu, sd, z, p = rt
            c, tag = verdict_colour(p)
            st.set("runs", "R = %d     E[R] = %.2f     sd = %.2f     Z = %+.3f  "
                           "  p = %.4f   %s" % (r, mu, sd, z, p, tag), c)
        else:
            st.set("runs", "-", MUTED)

        cs = chi2_uniform([n1, n0])
        if cs:
            x2, df, e, p = cs
            c, tag = verdict_colour(p)
            st.set("chi", "X2 = %.4f     df = %d     expected %.1f each     "
                          "p = %.4f   %s" % (x2, df, e, p, tag), c)

        sp = serial_pair_test(bits)
        if sp:
            counts, x2, df, e, p = sp
            c, tag = verdict_colour(p)
            st.set("serial", "00:%d  01:%d  10:%d  11:%d     X2 = %.4f  df = %d  "
                             "expected %.1f each     p = %.4f   %s"
                   % (counts[0], counts[1], counts[2], counts[3],
                      x2, df, e, p, tag), c)
        else:
            st.set("serial", "-", MUTED)

        h = shannon_bits([n1, n0])
        hexp = expected_sample_entropy(2, n)
        st.set("entropy", "%.6f bits per toss     maximum 1.000000     expected "
                          "for n=%d: %.6f     %.4f%% of maximum"
                          % (h, n, hexp, 100.0 * h))

        st.set("bytes", "%d bytes drawn from source     (1 bit per toss, "
                        "8 tosses per byte)" % self.engine.bytes_drawn, MUTED)

    # -- report --------------------------------------------------------------
    def _run_report(self):
        out = [self._report_header(), ""]
        out.append(self.values_text.get("1.0", "end-1c"))
        out.append("")
        out.append("RANDOMNESS QUALITY")
        out.append("-" * 74)
        for key, label in [("counts", "Balance"), ("longest", "Longest run"),
                           ("runs", "Runs test"), ("chi", "Chi-square df=1"),
                           ("serial", "Serial pair df=3"),
                           ("entropy", "Shannon entropy"),
                           ("bytes", "Source consumption")]:
            out.append("%-20s %s" % (label, self.stats.vars[key].get()))
        return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------
# DICE TAB

class DiceTab(SimTab):
    ROUNDS = 6
    PER_ROUND = 6
    NOUN = "roll"
    NOUN_PL = "rolls"
    RESET_LABEL = "Reroll"
    DEFAULT_SPEED = 5

    DIE = 52
    GAP = 10

    SPACE_ROUND = 6 ** 6
    SPACE_TOTAL = 6 ** 36

    def _build_body(self, parent):
        main = ttk.Frame(parent, style="Bg.TFrame")
        main.pack(fill="x", padx=12)

        left = ttk.Frame(main, style="Card.TFrame", padding=(14, 12))
        left.pack(side="left", fill="y")
        ttk.Label(left, text="DICE", style="H2.TLabel").pack(anchor="w")
        ttk.Label(left, text="rejection sampling  -  bytes 252-255 discarded so "
                             "every face is exactly 1/6",
                  style="Note.TLabel", wraplength=230, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.stage = tk.Canvas(left, width=232, height=232, bg=CARD,
                               highlightthickness=0, bd=0)
        self.stage.pack()
        self.face_var = tk.StringVar(value="")
        ttk.Label(left, textvariable=self.face_var, style="Face.TLabel").pack(
            pady=(6, 0))
        ttk.Label(left, textvariable=self.status_var, style="Note.TLabel",
                  wraplength=230, justify="left").pack(anchor="w", pady=(8, 0))
        ttk.Separator(left, orient="horizontal").pack(fill="x", pady=10)
        ttk.Label(left, text="OUTCOME SPACE", style="Key.TLabel").pack(anchor="w")
        ttk.Label(left, text="per round   6^6", style="Mono.TLabel").pack(anchor="w")
        ttk.Label(left, text=grouped(self.SPACE_ROUND), style="Mono2.TLabel").pack(
            anchor="w")
        ttk.Label(left, text="6 rounds   (6^6)^6 = 6^36", style="Mono.TLabel").pack(
            anchor="w", pady=(6, 0))
        ttk.Label(left, text=sci(self.SPACE_TOTAL), style="Big.TLabel").pack(anchor="w")

        right = ttk.Frame(main, style="Card.TFrame", padding=(14, 12))
        right.pack(side="left", fill="both", expand=True, padx=(12, 0))
        ttk.Label(right, text="6 ROUNDS  x  6 DICE  =  36 ROLLS", style="H2.TLabel").pack(
            anchor="w")
        ttk.Label(right, text="click a die to re-roll it        shift+click to play "
                              "onward from it", style="Note.TLabel").pack(
            anchor="w", pady=(2, 8))

        w = self.PER_ROUND * (self.DIE + self.GAP) + self.GAP
        h = self.DIE + 2 * self.GAP
        self.blocks = []
        self.round_val = []
        for r in range(self.ROUNDS):
            row = ttk.Frame(right, style="Card.TFrame")
            row.pack(anchor="w", pady=2)
            ttk.Label(row, text="R%d" % (r + 1), style="H3.TLabel", width=4).pack(
                side="left")
            cv = tk.Canvas(row, width=w, height=h, bg=CARD,
                           highlightthickness=0, bd=0, cursor="hand2")
            cv.pack(side="left")
            cv.bind("<Button-1>", lambda e, rr=r: self._cell_click(e, rr, False))
            cv.bind("<Shift-Button-1>", lambda e, rr=r: self._cell_click(e, rr, True))
            self.blocks.append(cv)
            v = tk.StringVar(value="-")
            ttk.Label(row, textvariable=v, style="Mono.TLabel").pack(
                side="left", padx=(14, 0))
            self.round_val.append(v)

        vp = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        vp.pack(fill="x", padx=12, pady=(10, 0))
        ttk.Label(vp, text="THE DRAW", style="H2.TLabel").pack(anchor="w")
        ttk.Label(vp, text="Faces 1-6 map to base-6 digits 0-5. The 36 dice read as "
                           "one 36-digit base-6 number - the outcome, drawn from a "
                           "space of 6^36.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.values_text = tk.Text(vp, height=17, bg=PANEL, fg=TEXT, bd=0,
                                   highlightthickness=1, highlightbackground=EDGE,
                                   highlightcolor=EDGE, insertbackground=TEXT,
                                   wrap="word", padx=12, pady=10, font=(MONO, 9))
        self.values_text.pack(fill="x")
        self.values_text.configure(state="disabled")

        sp = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        sp.pack(fill="x", padx=12, pady=(10, 14))
        ttk.Label(sp, text="RANDOMNESS QUALITY", style="H2.TLabel").pack(anchor="w")
        ttk.Label(sp, text="36 rolls is a small sample - expected count is 6.0 per "
                           "face, which is the minimum for chi-square to be "
                           "trustworthy, so treat one run as indicative rather than "
                           "proof. Rows carrying a p-value are hypothesis tests and "
                           "are what the verdict refers to; face counts and entropy "
                           "are descriptive. At n=36 the entropy estimate sits below "
                           "log2(6) even for a perfectly fair die - the expected "
                           "value shown is the honest comparison.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.stats = StatsTable(sp, [
            ("counts", "Face counts"),
            ("chi", "Chi-square, uniform  df=5"),
            ("longest", "Longest repeat run"),
            ("changes", "Adjacent changes"),
            ("entropy", "Shannon entropy"),
            ("bytes", "Source consumption"),
        ])
        self.stats.pack(fill="x")

    def _cell_click(self, event, rnd, shift):
        cv = self.blocks[rnd]
        step = self.DIE + self.GAP
        col = int((cv.canvasx(event.x) - self.GAP) // step)
        if not (0 <= col < self.PER_ROUND):
            return
        idx = rnd * self.PER_ROUND + col
        if shift:
            self.play_from(idx)
        else:
            self.retoss_cell(idx)

    def _paint_cell(self, idx):
        rnd, col = divmod(idx, self.PER_ROUND)
        cv = self.blocks[rnd]
        tag = "d%d" % col
        cv.delete(tag)
        step = self.DIE + self.GAP
        cx = self.GAP + col * step + self.DIE / 2.0
        cy = self.GAP + self.DIE / 2.0
        v = self.results[idx]
        if v is None:
            rounded_rect(cv, cx - self.DIE / 2, cy - self.DIE / 2,
                         cx + self.DIE / 2, cy + self.DIE / 2, 9,
                         fill=PANEL, outline=EDGE, width=1, tags=tag)
            cv.create_text(cx, cy, text="·", fill=DIM, font=(UI, 14), tags=tag)
        else:
            draw_die(cv, cx, cy, self.DIE, v, 0.0, tags=tag)

    def _new_value(self):
        return self.engine.die()

    def _draw_stage(self, t=None, value=None):
        cv = self.stage
        cv.delete("all")
        w = 232
        cx, cy = w / 2.0, w / 2.0 - 6
        size = 108.0

        if t is None:
            v = self.last_value
            angle = 0.0
            lift = 0.0
            idle = v is None
            face = v if v else 1
        else:
            idle = False
            angle = (4.0 * math.pi) * ease_out(t)
            lift = -math.sin(math.pi * t) * 26.0
            if t >= 0.78:
                face = value
                angle = (4.0 * math.pi) * ease_out(t)
            else:
                # tumble through faces; purely cosmetic, the result is already set
                face = 1 + int((t * 37.0)) % 6
        yc = cy + lift

        sh = 1.0 - min(1.0, abs(lift) / 30.0)
        cv.create_oval(cx - size * 0.55 * sh, cy + 74 - 8 * sh,
                       cx + size * 0.55 * sh, cy + 74 + 8 * sh,
                       fill="#0a0d12", outline="")

        if idle:
            rounded_rect(cv, cx - size / 2, yc - size / 2, cx + size / 2,
                         yc + size / 2, 16, fill=PANEL, outline=EDGE, width=2)
            cv.create_text(cx, yc, text="?", fill=DIM, font=(UI, 40, "bold"))
            self.face_var.set("")
        else:
            draw_die(cv, cx, yc, size, face, angle)
            self.face_var.set(str(face))

    def _faces_of(self, rnd):
        lo = rnd * self.PER_ROUND
        return self.results[lo:lo + self.PER_ROUND]

    def _refresh_values(self):
        lines = []
        all_faces = []
        complete = 0
        for r in range(self.ROUNDS):
            faces = self._faces_of(r)
            shown = " ".join(str(f) if f else "·" for f in faces)
            done = all(f is not None for f in faces)
            if done:
                complete += 1
                digits = [f - 1 for f in faces]
                val = 0
                for d in digits:
                    val = val * 6 + d
                self.round_val[r].set("base6 %s  =  %s"
                                      % ("".join(str(d) for d in digits),
                                         grouped(val)))
                lines.append("ROUND %d   faces %s     base-6 digits %s"
                             % (r + 1, shown, "".join(str(d) for d in digits)))
                lines.append("          value %s   of 6^6 = %s  (range 0 - %s)"
                             % (grouped(val), grouped(self.SPACE_ROUND),
                                grouped(self.SPACE_ROUND - 1)))
            else:
                n = sum(1 for f in faces if f is not None)
                self.round_val[r].set("%d / 6" % n)
                lines.append("ROUND %d   faces %s     incomplete (%d / 6)"
                             % (r + 1, shown, n))
            lines.append("")
            all_faces.extend(faces)

        lines.append("-" * 88)
        if complete == self.ROUNDS:
            digits = [f - 1 for f in all_faces]
            val = 0
            for d in digits:
                val = val * 6 + d
            ds = "".join(str(d) for d in digits)
            lines.append("FULL 36-DIE DRAW")
            lines.append("  faces   " + " ".join(str(f) for f in all_faces))
            lines.append("  base-6  " + ds)
            lines.append("  int     %s" % grouped(val))
            lines.append("")
            lines.append("  space 6^36 = %s" % grouped(self.SPACE_TOTAL))
            lines.append("             = %s" % sci(self.SPACE_TOTAL))
            lines.append("        this draw is 1 of those %s possibilities;"
                         % sci(self.SPACE_TOTAL, 5))
            lines.append("        the chance of repeating it is 1 in %s."
                         % sci(self.SPACE_TOTAL, 5))
        else:
            n = sum(1 for f in self.results if f is not None)
            lines.append("FULL 36-DIE DRAW      incomplete  (%d / 36 rolls)" % n)
            lines.append("")
            lines.append("  space 6^36 = %s" % grouped(self.SPACE_TOTAL))
            lines.append("             = %s" % sci(self.SPACE_TOTAL))
        self._set_text(self.values_text, "\n".join(lines))

    def _refresh_stats(self):
        faces = [f for f in self.results if f is not None]
        n = len(faces)
        st = self.stats
        if n < 2:
            for k in ("counts", "chi", "longest", "changes", "entropy"):
                st.set(k, "-", MUTED)
            st.set("bytes", "%d bytes drawn, %d discarded by the rejection sampler"
                            % (self.engine.bytes_drawn, self.engine.rejected), MUTED)
            return

        counts = [faces.count(f) for f in range(1, 7)]
        st.set("counts", "   ".join("%d:%d" % (f, counts[f - 1]) for f in range(1, 7))
                         + "     expected %.2f each  (n=%d)" % (n / 6.0, n))

        cs = chi2_uniform(counts)
        if cs:
            x2, df, e, p = cs
            c, tag = verdict_colour(p)
            st.set("chi", "X2 = %.4f     df = %d     expected %.2f each     "
                          "p = %.4f   %s" % (x2, df, e, p, tag), c)

        lr = longest_run(faces)
        occ = expected_run_occurrences(n, lr, 6)
        c = GOOD if occ >= 0.05 else (WARN if occ >= 0.005 else BAD)
        st.set("longest", "%d identical in a row     expected occurrences of a run "
                          "this long in %d rolls: %.4f" % (lr, n, occ), c)

        ch = sum(1 for i in range(1, n) if faces[i] != faces[i - 1])
        m = n - 1
        exp_ch = m * 5.0 / 6.0
        pch = binom_two_sided_p(ch, m, 5.0 / 6.0)
        c, tag = verdict_colour(pch)
        st.set("changes", "%d of %d adjacent pairs differ     expected %.2f     "
                          "exact binomial p = %.4f   %s"
                          % (ch, m, exp_ch, pch if pch is not None else float("nan"),
                             tag), c)

        h = shannon_bits(counts)
        hmax = math.log2(6)
        hexp = expected_sample_entropy(6, n)
        st.set("entropy", "%.6f bits per roll     maximum %.6f     expected for "
                          "n=%d: %.6f     %.4f%% of maximum"
                          % (h, hmax, n, hexp, 100.0 * h / hmax))

        rate = (100.0 * self.engine.rejected / self.engine.bytes_drawn
                if self.engine.bytes_drawn else 0.0)
        st.set("bytes", "%d bytes drawn, %d discarded (%.2f%%, theoretical 1.5625%%) "
                        "- this is what removes the modulo bias"
                        % (self.engine.bytes_drawn, self.engine.rejected, rate), MUTED)

    def _run_report(self):
        out = [self._report_header(), ""]
        out.append(self.values_text.get("1.0", "end-1c"))
        out.append("")
        out.append("RANDOMNESS QUALITY")
        out.append("-" * 74)
        for key, label in [("counts", "Face counts"), ("chi", "Chi-square df=5"),
                           ("longest", "Longest repeat"),
                           ("changes", "Adjacent changes"),
                           ("entropy", "Shannon entropy"),
                           ("bytes", "Source consumption")]:
            out.append("%-20s %s" % (label, self.stats.vars[key].get()))
        return "\n".join(out) + "\n"

# ===========================================================================
# BIP-39 TAB
# ===========================================================================
BIP39_LENGTHS = [
    ("12 words   -   128-bit entropy + 4-bit checksum", 12),
    ("15 words   -   160-bit entropy + 5-bit checksum", 15),
    ("18 words   -   192-bit entropy + 6-bit checksum", 18),
    ("21 words   -   224-bit entropy + 7-bit checksum", 21),
    ("24 words   -   256-bit entropy + 8-bit checksum", 24),
]

SAFETY_TEXT = (
    "These are REAL, spendable keys computed to the published standards. A phrase "
    "generated on a general-purpose PC is not as safe as one generated inside a "
    "hardware wallet's secure element: this machine has an operating system, a "
    "screen buffer, a clipboard and possibly a network. Use this tab to learn the "
    "mechanism and to cross-check that a device and the standard agree. For a "
    "wallet you intend to fund, generate the phrase on the device itself and "
    "verify it here only if you accept the exposure."
)


class Bip39Tab(ttk.Frame):
    """BIP-39 mnemonic generation, checksum validation and HD address derivation."""

    def __init__(self, parent, app):
        super().__init__(parent, style="Bg.TFrame")
        self.app = app
        self.words = []
        self.entropy = b""
        self.engine = None
        self.entropy_origin = "-"

        self.mode_var = tk.StringVar(value=MODE_OS_SEED)
        self.seed_var = tk.StringVar(value="")
        self.len_var = tk.StringVar(value=BIP39_LENGTHS[4][0])
        self.pass_var = tk.StringVar(value="")
        self.acct_var = tk.StringVar(value="0")
        self.show_priv = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="no phrase yet  -  press Generate")
        self.engine_var = tk.StringVar(value="")
        self.verify_var = tk.StringVar(value="")

        self.scroll = Scrollable(self)
        self.scroll.pack(fill="both", expand=True)
        body = self.scroll.inner

        self._build_banner(body)
        self._build_controls(body)
        self._build_phrase(body)
        self._build_math(body)
        self._build_addresses(body)
        self.new_engine()
        self.clear()

    # -- engine -------------------------------------------------------------
    def new_engine(self):
        self.engine = Engine(self.mode_var.get(), self.seed_var.get())
        rep = "reproducible" if self.engine.reproducible else "not reproducible"
        self.engine_var.set("key fingerprint  %s        %s"
                            % (self.engine.fingerprint, rep))

    def on_source_change(self, *_a):
        self.new_engine()
        self.note_var.set(MODE_NOTE.get(self.mode_var.get(), ""))

    def word_count(self):
        for label, n in BIP39_LENGTHS:
            if label == self.len_var.get():
                return n
        return 24

    def account(self):
        try:
            return max(0, min(2 ** 31 - 1, int(self.acct_var.get())))
        except ValueError:
            return 0

    # -- layout -------------------------------------------------------------
    def _build_banner(self, parent):
        bar = tk.Frame(parent, bg="#3a2c10", highlightthickness=1,
                       highlightbackground="#7a5d1c")
        bar.pack(fill="x", padx=12, pady=(12, 8))
        tk.Label(bar, text="  READ THIS FIRST", bg="#3a2c10", fg=UP_C,
                 font=(UI, 10, "bold")).pack(anchor="w", pady=(8, 0), padx=10)
        tk.Label(bar, text=SAFETY_TEXT, bg="#3a2c10", fg="#e0cfa0",
                 font=(UI, 9), wraplength=1180, justify="left").pack(
            anchor="w", padx=10, pady=(3, 9))

    def _build_controls(self, parent):
        bar = ttk.Frame(parent, style="Card.TFrame", padding=(14, 11))
        bar.pack(fill="x", padx=12, pady=(0, 8))

        ttk.Label(bar, text="Length", style="Key.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        cb = ttk.Combobox(bar, textvariable=self.len_var,
                          values=[l for l, _ in BIP39_LENGTHS], state="readonly",
                          width=44, style="Dark.TCombobox")
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", lambda e: self.clear())

        ttk.Label(bar, text="Account", style="Key.TLabel").grid(
            row=0, column=2, sticky="e", padx=(20, 8))
        ae = ttk.Entry(bar, textvariable=self.acct_var, width=6, style="Dark.TEntry")
        ae.grid(row=0, column=3, sticky="w")
        ae.bind("<Return>", lambda e: self.refresh_addresses())

        ttk.Label(bar, text="Passphrase  (optional 25th word)",
                  style="Key.TLabel").grid(row=0, column=4, sticky="e", padx=(20, 8))
        pe = ttk.Entry(bar, textvariable=self.pass_var, width=22, style="Dark.TEntry")
        pe.grid(row=0, column=5, sticky="w")
        pe.bind("<Return>", lambda e: self.refresh_addresses())

        ttk.Label(bar, text="Source", style="Key.TLabel").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=(10, 0))
        cb2 = ttk.Combobox(bar, textvariable=self.mode_var, values=MODES,
                           state="readonly", width=44, style="Dark.TCombobox")
        cb2.grid(row=1, column=1, sticky="w", pady=(10, 0))
        cb2.bind("<<ComboboxSelected>>", self.on_source_change)

        ttk.Label(bar, text="Initial seed", style="Key.TLabel").grid(
            row=1, column=2, sticky="e", padx=(20, 8), pady=(10, 0))
        se = ttk.Entry(bar, textvariable=self.seed_var, width=22, style="Dark.TEntry")
        se.grid(row=1, column=3, columnspan=2, sticky="w", pady=(10, 0))
        se.bind("<Return>", self.on_source_change)
        ttk.Button(bar, text="Apply seed", style="Ghost.TButton",
                   command=self.on_source_change).grid(row=1, column=5, sticky="w",
                                                       pady=(10, 0))

        btns = ttk.Frame(bar, style="Card.TFrame")
        btns.grid(row=2, column=0, columnspan=6, sticky="w", pady=(12, 0))
        ttk.Button(btns, text="Generate phrase", style="Accent.TButton",
                   command=self.generate).pack(side="left")
        ttk.Button(btns, text="Use Coin tab tosses", style="Ghost.TButton",
                   command=self.from_coin).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="Roll dice for entropy", style="Ghost.TButton",
                   command=self.from_dice).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="Clear", style="Ghost.TButton",
                   command=self.clear).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(btns, text="Show private keys", variable=self.show_priv,
                        style="Dark.TCheckbutton",
                        command=self.refresh_addresses).pack(side="left", padx=(24, 0))
        ttk.Button(btns, text="Copy all", style="Ghost.TButton",
                   command=self.copy_all).pack(side="left", padx=(24, 0))
        ttk.Button(btns, text="Save run", style="Ghost.TButton",
                   command=self.save_run).pack(side="left", padx=(8, 0))

        self.note_var = tk.StringVar(value=MODE_NOTE[MODE_OS_SEED])
        ttk.Label(bar, textvariable=self.note_var, style="Note.TLabel",
                  wraplength=1120, justify="left").grid(
            row=3, column=0, columnspan=6, sticky="w", pady=(11, 0))
        ttk.Label(bar, textvariable=self.engine_var, style="Mono2.TLabel").grid(
            row=4, column=0, columnspan=6, sticky="w", pady=(5, 0))
        ttk.Label(bar, textvariable=self.status_var, style="Mono.TLabel").grid(
            row=5, column=0, columnspan=6, sticky="w", pady=(5, 0))

    def _build_phrase(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        card.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(card, text="THE PHRASE", style="H2.TLabel").pack(anchor="w")
        ttk.Label(card, text="Each word carries exactly 11 bits, because the list "
                             "holds 2^11 = 2048 words. Word order is part of the "
                             "secret.", style="Note.TLabel").pack(anchor="w",
                                                                  pady=(2, 8))
        self.chip_frame = ttk.Frame(card, style="Card.TFrame")
        self.chip_frame.pack(anchor="w")
        self.chip_vars = []

        ver = ttk.Frame(card, style="Card.TFrame")
        ver.pack(fill="x", pady=(12, 0))
        ttk.Separator(ver, orient="horizontal").pack(fill="x", pady=(0, 10))
        ttk.Label(ver, text="VERIFY AN EXISTING PHRASE", style="H3.TLabel").pack(
            anchor="w")
        ttk.Label(ver, text="Paste a phrase from a hardware wallet to check every "
                            "word against the 2048-word list, recompute its "
                            "checksum, and derive the same addresses.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 6))
        row = ttk.Frame(ver, style="Card.TFrame")
        row.pack(fill="x")
        e = ttk.Entry(row, textvariable=self.verify_var, style="Dark.TEntry",
                      font=(MONO, 9))
        e.pack(side="left", fill="x", expand=True)
        e.bind("<Return>", lambda ev: self.verify())
        ttk.Button(row, text="Check phrase", style="Ghost.TButton",
                   command=self.verify).pack(side="left", padx=(8, 0))

    def _build_math(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        card.pack(fill="x", padx=12, pady=(0, 8))
        ttk.Label(card, text="ENTROPY, CHECKSUM AND OUTCOME SPACE",
                  style="H2.TLabel").pack(anchor="w")
        ttk.Label(card, text="The checksum is derived from the entropy, so it adds "
                             "no secrecy: it only catches a mistyped or "
                             "transposed word. The number of VALID phrases equals "
                             "the entropy space, never the raw word-sequence count.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 8))
        self.math_text = tk.Text(card, height=16, bg=PANEL, fg=TEXT, bd=0,
                                 highlightthickness=1, highlightbackground=EDGE,
                                 highlightcolor=EDGE, wrap="word", padx=12, pady=10,
                                 font=(MONO, 9))
        self.math_text.pack(fill="x")
        self.math_text.configure(state="disabled")

    def _build_addresses(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=(14, 12))
        card.pack(fill="x", padx=12, pady=(0, 14))
        ttk.Label(card, text="DERIVED KEYS AND ADDRESSES", style="H2.TLabel").pack(
            anchor="w")
        ttk.Label(card, text="mnemonic -> PBKDF2-HMAC-SHA512 (2048 rounds) -> "
                             "512-bit seed -> BIP-32 / SLIP-10 -> private key -> "
                             "public key -> address. Bitcoin, Ethereum and Mina "
                             "derive on secp256k1; Solana, Aptos and Sui use "
                             "ed25519; Mina then maps onto the Pallas curve.",
                  style="Note.TLabel", wraplength=1120, justify="left").pack(
            anchor="w", pady=(2, 8))

        grid = ttk.Frame(card, style="Panel.TFrame", padding=(12, 10))
        grid.pack(fill="x")
        for c, (txt, w) in enumerate([("CHAIN", 34), ("PATH", 22), ("ADDRESS", 0)]):
            ttk.Label(grid, text=txt, style="Key.TLabel").grid(
                row=0, column=c, sticky="w", padx=(0, 12), pady=(0, 6))
        self.addr_rows = {}
        r = 1
        for key, label, template, curve in DERIVATIONS:
            ttk.Label(grid, text=label, style="Mono.TLabel").grid(
                row=r, column=0, sticky="w", padx=(0, 12), pady=2)
            pv = tk.StringVar(value="-")
            ttk.Label(grid, textvariable=pv, style="Mono2.TLabel").grid(
                row=r, column=1, sticky="w", padx=(0, 12), pady=2)
            av = tk.StringVar(value="-")
            ae = ttk.Entry(grid, textvariable=av, style="RO.TEntry",
                           font=(MONO, 9), state="readonly", width=66)
            ae.grid(row=r, column=2, sticky="we", pady=2)
            kv = tk.StringVar(value="")
            ke = ttk.Entry(grid, textvariable=kv, style="RO.TEntry",
                           font=(MONO, 9), state="readonly", width=66)
            ke.grid(row=r + 1, column=2, sticky="we", pady=(0, 6))
            ke.grid_remove()
            self.addr_rows[key] = (pv, av, kv, ke)
            r += 2
        grid.columnconfigure(2, weight=1)

    # -- actions ------------------------------------------------------------
    def _set_text(self, widget, content):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(height=max(6, min(40, content.count("\n") + 1)),
                         state="disabled")

    def clear(self):
        self.words = []
        self.entropy = b""
        self.entropy_origin = "-"
        self.status_var.set("no phrase yet  -  press Generate")
        self._render_chips()
        self._render_math()
        self.refresh_addresses()

    def generate(self):
        n = self.word_count()
        ent_bits, _, _ = words_to_bits(n)
        self.entropy = bytes(self.engine.next_byte() for _ in range(ent_bits // 8))
        self.entropy_origin = "%s  (%d bytes)" % (self.mode_var.get().split("  ")[0],
                                                  ent_bits // 8)
        self._apply_entropy()

    def from_coin(self):
        """Use the Coin tab's tosses directly. 1 toss = 1 bit, so 256 tosses is
        exactly a 24-word seed with nothing thrown away and nothing added."""
        coin = getattr(self.app, "coin", None)
        if coin is None:
            return
        bits = [b for b in coin.results if b is not None]
        n = self.word_count()
        need, _, _ = words_to_bits(n)
        if len(bits) < need:
            messagebox.showwarning(
                APP_TITLE,
                "A %d-word phrase needs %d bits of entropy, but the Coin tab has "
                "only %d committed tosses.\n\nRun the Coin tab to at least %d "
                "tosses (press Play, or Fill rest), then import again."
                % (n, need, len(bits), need))
            return
        use = bits[:need]
        self.entropy = int("".join(str(b) for b in use), 2).to_bytes(need // 8, "big")
        self.entropy_origin = ("Coin tab, first %d of %d tosses, used as raw bits"
                               % (need, len(bits)))
        self._apply_entropy()

    def from_dice(self):
        """Roll dice from the current source and fold them into entropy.

        A die yields log2(6) = 2.585 bits, so 36 dice hold only 93 bits - not
        enough for even a 12-word phrase. Roll the number that actually covers
        the requirement and condense with SHA-256, the method Coldcard and the
        usual dice-entropy tools use.
        """
        n = self.word_count()
        need, _, _ = words_to_bits(n)
        count = int(math.ceil(need / math.log2(6)))
        rolls = [self.engine.die() for _ in range(count)]
        digits = "".join(str(d) for d in rolls)
        self.entropy = hashlib.sha256(digits.encode("ascii")).digest()[:need // 8]
        self.entropy_origin = (
            "%d dice = %.1f bits (>= %d needed), condensed with SHA-256\n"
            "         rolls: %s" % (count, count * math.log2(6), need, digits))
        self._apply_entropy()

    def _apply_entropy(self):
        self.words = entropy_to_mnemonic(self.entropy)
        self.status_var.set("generated %d words  -  %d-bit entropy  -  checksum valid"
                            % (len(self.words), len(self.entropy) * 8))
        self._render_chips()
        self._render_math()
        self.refresh_addresses()

    def verify(self):
        raw = self.verify_var.get().replace(",", " ").replace("\n", " ").strip()
        words = [w.strip().lower() for w in raw.split() if w.strip()]
        if not words:
            messagebox.showinfo(APP_TITLE, "Paste a 12, 15, 18, 21 or 24 word "
                                           "phrase into the box first.")
            return
        unknown = [w for w in words if w not in WORD_INDEX]
        if unknown:
            messagebox.showerror(
                APP_TITLE,
                "These are not in the BIP-39 English wordlist:\n\n  %s\n\n"
                "Every word must come from the official 2048-word list."
                % ", ".join(unknown[:12]))
            self.status_var.set("verify FAILED  -  %d word(s) not in the wordlist"
                                % len(unknown))
            return
        try:
            self.entropy = mnemonic_to_entropy(words)
        except ValueError as exc:
            messagebox.showerror(APP_TITLE, "Checksum check failed.\n\n%s" % exc)
            self.status_var.set("verify FAILED  -  %s" % exc)
            self.words = words
            self._render_chips()
            return
        self.words = words
        for label, cnt in BIP39_LENGTHS:
            if cnt == len(words):
                self.len_var.set(label)
        self.entropy_origin = "pasted phrase, checksum verified"
        self.status_var.set("verify PASSED  -  %d words, %d-bit entropy, checksum "
                            "correct" % (len(words), len(self.entropy) * 8))
        self._render_chips()
        self._render_math()
        self.refresh_addresses()

    # -- rendering ----------------------------------------------------------
    def _render_chips(self):
        for w in self.chip_frame.winfo_children():
            w.destroy()
        if not self.words:
            ttk.Label(self.chip_frame, text="(empty)", style="Note.TLabel").grid(
                row=0, column=0, sticky="w")
            return
        cols = 4
        for i, word in enumerate(self.words):
            r, c = divmod(i, cols)
            cell = tk.Frame(self.chip_frame, bg=PANEL, highlightthickness=1,
                            highlightbackground=EDGE)
            cell.grid(row=r, column=c, sticky="we", padx=(0, 8), pady=3)
            tk.Label(cell, text="%2d" % (i + 1), bg=PANEL, fg=DIM,
                     font=(MONO, 9), width=3).pack(side="left", padx=(6, 2), pady=4)
            tk.Label(cell, text=word, bg=PANEL, fg=UP_C,
                     font=(MONO, 11, "bold"), width=11, anchor="w").pack(
                side="left", padx=(2, 6), pady=4)
            tk.Label(cell, text="%04d" % WORD_INDEX[word], bg=PANEL, fg=DIM,
                     font=(MONO, 8)).pack(side="left", padx=(0, 8), pady=4)

    def _render_math(self):
        if not self.words:
            self._set_text(self.math_text,
                           "No phrase loaded.\n\n"
                           "Wordlist  2048 words = 2^11, so 11 bits per word\n"
                           "SHA-256   %s\n"
                           "          matches the official english.txt: %s"
                           % (WORDLIST_SHA256,
                              "yes" if WORDLIST_SHA256 == OFFICIAL_WORDLIST_SHA256
                              else "NO"))
            return
        n = len(self.words)
        ent_bits, cs_bits, total = words_to_bits(n)
        cs_val, _ = checksum_bits_of(self.entropy)
        full = hashlib.sha256(self.entropy).hexdigest()
        idx = [WORD_INDEX[w] for w in self.words]
        L = []
        L.append("ENTROPY SOURCE   %s" % self.entropy_origin)
        L.append("")
        L.append("entropy   %d bits   %s" % (ent_bits, self.entropy.hex()))
        L.append("SHA-256   %s" % full)
        L.append("checksum  first %d bits of that hash = %s   (0x%X)"
                 % (cs_bits, format(cs_val, "0%db" % cs_bits), cs_val))
        L.append("total     %d + %d = %d bits = %d words x 11 bits"
                 % (ent_bits, cs_bits, total, n))
        L.append("")
        L.append("11-BIT GROUPS")
        for i in range(0, n, 6):
            grp = idx[i:i + 6]
            L.append("  %2d-%2d  %s" % (i + 1, i + len(grp),
                                        "  ".join("%s=%4d" % (
                                            format(v, "011b"), v) for v in grp)))
        L.append("")
        L.append("OUTCOME SPACE")
        L.append("  word sequences of this length   2048^%d = 2^%d = %s"
                 % (n, total, sci(2 ** total)))
        L.append("  VALID phrases (checksum holds)  2^%d = %s"
                 % (ent_bits, grouped(2 ** ent_bits)))
        L.append("                                  = %s" % sci(2 ** ent_bits))
        L.append("  only 1 in 2^%d = %d random word sequences carries a correct"
                 % (cs_bits, 2 ** cs_bits))
        L.append("  checksum, so the security is 2^%d, NOT 2^%d. The checksum"
                 % (ent_bits, total))
        L.append("  detects typing errors; it adds no secrecy.")
        if n == 24:
            L.append("")
            L.append("  2^256 here is the same space as 256 fair coin tosses -")
            L.append("  the Coin tab's 4 x 64 run is exactly one 24-word seed.")
        self._set_text(self.math_text, "\n".join(L))

    def refresh_addresses(self):
        show = self.show_priv.get()
        if not self.words or not self.entropy:
            for key, (pv, av, kv, ke) in self.addr_rows.items():
                pv.set("-")
                av.set("-")
                kv.set("")
                ke.grid_remove()
            return
        seed = mnemonic_to_seed(self.words, self.pass_var.get())
        self.derived = derive_all(seed, self.account())
        for rec in self.derived:
            pv, av, kv, ke = self.addr_rows[rec["key"]]
            pv.set(rec["path"])
            av.set(rec["addr"])
            if show:
                kv.set("priv  " + rec["priv_disp"])
                ke.grid()
            else:
                kv.set("")
                ke.grid_remove()

    # -- output -------------------------------------------------------------
    def _report(self, redact=True):
        L = ["%s %s  -  BIP-39 run" % (APP_TITLE, APP_VER), "=" * 74,
             "generated      %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
             "source         %s" % self.entropy_origin,
             "wordlist       official BIP-39 English, SHA-256 %s" % WORDLIST_SHA256,
             ""]
        if not self.words:
            L.append("(no phrase)")
            return "\n".join(L) + "\n"
        n = len(self.words)
        ent_bits, cs_bits, total = words_to_bits(n)
        L.append("PHRASE  (%d words)" % n)
        for i in range(0, n, 4):
            L.append("  " + "  ".join("%2d %-9s" % (i + j + 1, self.words[i + j])
                                      for j in range(min(4, n - i))))
        L.append("")
        L.append("entropy   %d bits  %s" % (ent_bits, self.entropy.hex()))
        L.append("checksum  %d bits, verified" % cs_bits)
        L.append("valid-phrase space  2^%d = %s" % (ent_bits, grouped(2 ** ent_bits)))
        L.append("passphrase %s" % ("(set)" if self.pass_var.get() else "(none)"))
        L.append("account    %d" % self.account())
        L.append("")
        L.append("ADDRESSES")
        for rec in getattr(self, "derived", []):
            L.append("  %-36s %-22s %s" % (rec["label"], rec["path"], rec["addr"]))
        L.append("")
        if redact:
            L.append("Private keys were NOT written to this file.")
            L.append("Tick 'Show private keys' and save again if you need them -")
            L.append("but a plaintext file holding them is a plaintext wallet.")
        else:
            L.append("PRIVATE KEYS  -- ANYONE WITH THESE CAN SPEND THE FUNDS")
            for rec in getattr(self, "derived", []):
                L.append("  %-36s %s" % (rec["label"], rec["priv_disp"]))
        return "\n".join(L) + "\n"

    def copy_all(self):
        self.clipboard_clear()
        self.clipboard_append(self._report(redact=not self.show_priv.get()))
        self.app.flash("BIP-39 run copied to clipboard.")

    def save_run(self):
        if not self.words:
            messagebox.showinfo(APP_TITLE, "Generate or verify a phrase first.")
            return
        try:
            base = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base = os.getcwd()
        folder = os.path.join(base, "runs")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "bip39_%s.txt"
                            % datetime.now().strftime("%Y%m%d_%H%M%S"))
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self._report(redact=not self.show_priv.get()))
        except OSError as exc:
            messagebox.showerror(APP_TITLE, "Could not save:\n%s" % exc)
            return
        self.app.flash("Saved  ->  runs\\%s" % os.path.basename(path))


# ----------------------------------------------------------------------------
# Application

# ----------------------------------------------------------------------------
# Application
# ----------------------------------------------------------------------------
class App(KernelApp):
    def __init__(self):
        super().__init__(
            "%s  %s   -   coin 2^256 | dice 6^36 | BIP-39" % (APP_TITLE, APP_VER),
            "real entropy, unbiased extraction, measured output")
        self.coin = CoinTab(self.nb, self)
        self.dice = DiceTab(self.nb, self)
        self.bip39 = Bip39Tab(self.nb, self)
        self.nb.add(self.coin, text="  COIN    4 x 64 = 256    2^256  ")
        self.nb.add(self.dice, text="  DICE    6 x 6 = 36    6^36  ")
        self.nb.add(self.bip39, text="  BIP-39    12 / 15 / 18 / 21 / 24 words  ")
        self.closeables = [self.coin, self.dice]
        self.add_about_tab(
            "%s %s" % (APP_TITLE, APP_VER),
            APP_VER,
            blurb=("Coin (2^256), dice (6^36) and BIP-39 seed phrases, drawn "
                   "from the OS CSPRNG, extracted without bias, and scored "
                   "with exact p-values. No third-party packages, no network."),
            notes=(
                ("KEYS: the BIP-39 tab produces real, spendable keys. A "
                 "phrase generated on a general-purpose PC is not as safe as "
                 "one generated inside a hardware wallet's secure element - "
                 "this machine has an OS, a screen buffer, a clipboard and "
                 "probably a network. For a wallet you intend to fund, "
                 "generate on the device itself.", WARN),
                "SOURCE: this is free software and you are entitled to the "
                "source. It is the three files beside this one - "
                "real_random_simulator.py, rrs_kernel.py and the .bat "
                "launcher - with no build step, no compiled component and no "
                "third-party package.",
            ))


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    try:
        app = App()
        app.mainloop()
    except Exception:
        # Launched by double-click (pythonw) there is no console to print a
        # traceback to, so a crash would otherwise look like "nothing
        # happened". Show it in a window, and still write it to stderr for
        # anyone who did start this from a terminal.
        import traceback
        tb = traceback.format_exc()
        try:
            sys.stderr.write(tb)
        except Exception:
            pass
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "%s %s  -  启动失败 / failed to start" % (APP_TITLE, APP_VER),
                tb[-3000:])
            root.destroy()
        except Exception:
            pass
        raise SystemExit(1)


if __name__ == "__main__":
    main()

