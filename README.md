# Seat Math

Seat apportionment arithmetic. The same ballots give the biggest party 5 of 10 seats under D'Hondt and largest remainder, but 4 under Sainte-Lague.

## What it computes

Give it vote counts for 1 to 8 parties (A, B, C and so on) and a number of seats:

- **The remainder truth** - largest remainder method: whole seats from each share, then the biggest leftovers take the rest.
- **The D'Hondt truth** - highest averages with divisors 1, 2, 3 and so on.
- **The Sainte-Lague truth** - highest averages with divisors 1, 3, 5 and so on.

Ties are reported, never broken: if parties share the same remainder or quotient for the last seats, those seats are shown as undecided. Vote counts go up to 1000000000 each, seats up to 1000.

## Boundary

Arithmetic only. It splits seats by three textbook formulas using the owner's own vote counts. It does not know any country's, club's or company's real rules (thresholds, districts, tie-breaks) and gives no verdict on which method is fair or right.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic (BigInt votes, sorted quotient list, cross-multiplied comparisons).
- `oracle.py` - the Python mirror (Fractions, one round of seats at a time) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (132 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/seatmath/
Repo: https://github.com/iLanis-agent/seatmath
