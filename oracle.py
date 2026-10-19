#!/usr/bin/env python3
# Seat Math oracle - mirrors engine.js. Seats are handed out one round at a time with Fractions, not by sorting every quotient.
import json, re
from fractions import Fraction
from math import floor

VOTES_ERR = "enter 1 to 8 vote counts separated by commas, each a whole number from 0 to 1000000000"
TOTAL_ERR = "the total votes must be above 0"
SEATS_ERR = "the seats must be a whole number from 1 to 1000"

def parse(votes, seats):
    t = votes.strip() if isinstance(votes, str) else ""
    parts = [x.strip() for x in t.split(",")]
    if not 1 <= len(parts) <= 8: raise ValueError(VOTES_ERR)
    v = []
    for x in parts:
        if not re.fullmatch(r"[0-9]{1,10}", x) or int(x) > 10**9: raise ValueError(VOTES_ERR)
        v.append(int(x))
    z = seats.strip() if isinstance(seats, str) else ""
    if not re.fullmatch(r"[0-9]{1,6}", z) or not 1 <= int(z) <= 1000: raise ValueError(SEATS_ERR)
    if sum(v) == 0: raise ValueError(TOTAL_ERR)
    return v, int(z)

def name(i): return chr(65 + i)
def join(ix):
    n = [name(i) for i in ix]
    return n[0] if len(n) == 1 else ", ".join(n[:-1]) + " and " + n[-1]
def seatw(n): return f"{n} seat" + ("" if n == 1 else "s")
def render(label, s, counts, tied, room, what):
    out = f"{label}, {seatw(s)}: " + ", ".join(f"{name(i)} {c}" for i, c in enumerate(counts)) + "."
    if tied:
        out += f" {seatw(room)} {'is' if room == 1 else 'are'} undecided because {join(tied)} tie (same {what})."
    return out

def remainder(votes, seats):
    v, s = parse(votes, seats)
    total = sum(v)
    quota = Fraction(total, s)
    counts = [floor(Fraction(x) / quota) for x in v]
    rems = [Fraction(x) / quota - c for x, c in zip(v, counts)]
    left = s - sum(counts)
    tied = []; room = 0
    while left > 0:
        best = max(rems)
        group = [i for i, r in enumerate(rems) if r == best]
        if len(group) <= left:
            for i in group:
                counts[i] += 1; rems[i] = Fraction(-1)
            left -= len(group)
        else:
            tied, room = group, left
            break
    return render("Largest remainder", s, counts, tied, room, "remainder")

def averages(label, votes, seats, divisor):
    v, s = parse(votes, seats)
    counts = [0] * len(v)
    left = s; tied = []; room = 0
    while left > 0:
        q = [Fraction(x, divisor(c)) if x > 0 else Fraction(-1) for x, c in zip(v, counts)]
        best = max(q)
        group = [i for i, x in enumerate(q) if x == best]
        if len(group) <= left:
            for i in group: counts[i] += 1
            left -= len(group)
        else:
            tied, room = group, left
            break
    return render(label, s, counts, tied, room, "quotient")

def dhondt(votes, seats): return averages("D'Hondt", votes, seats, lambda c: c + 1)
def lagu(votes, seats): return averages("Sainte-Lague", votes, seats, lambda c: 2 * c + 1)

FNS = {"remainderTruth": remainder, "dhondtTruth": dhondt, "laguTruth": lagu}
INPUTS = [
    ["47000, 16000, 15800, 12000, 6100, 3100", "10"], ["100000,80000,30000,20000", "8"], ["100,100,50", "2"], ["100,100,50", "3"], ["10,10,10", "1"],
    ["10,10,10", "2"], ["10,10,10", "3"], ["0,5", "3"], ["5", "4"], ["1,1", "1"],
    ["1,1", "2"], ["3,1", "1"], ["3,1", "4"], ["3,1", "100"], ["7,7,7,7,7,7,7,7", "8"],
    ["7,7,7,7,7,7,7,7", "4"], ["1000000000,1000000000,1", "1000"], ["1000000000", "1000"], ["999999999,1", "10"], ["60,30,10", "10"],
    ["55,25,20", "5"], ["34,33,33", "10"], ["50,50", "7"], ["1,2,3,4,5,6,7,8", "20"], ["340,330,330", "1"],
    ["0,0,5,0", "2"], ["12,0,12", "5"], ["9,3", "4"], ["9,3", "5"], [" 100 , 200 ", " 3 "],
    ["", "5"], ["1,2,3,4,5,6,7,8,9", "5"], ["a,b", "5"], ["1,,2", "5"], ["1.5,2", "5"],
    ["-1,2", "5"], ["1000000001,2", "5"], ["0,0", "5"], ["0", "5"], ["10,20", "0"],
    ["10,20", "1001"], ["10,20", "x"], ["10,20", ""], ["10,20", "2.5"],
]
CASES = [(fn, a) for a in INPUTS for fn in ("remainderTruth", "dhondtTruth", "laguTruth")]
out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
