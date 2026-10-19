// Seat Math engine: exact seat apportionment on BigInt vote counts. Ties are reported, never broken.
var VOTES_ERR = "enter 1 to 8 vote counts separated by commas, each a whole number from 0 to 1000000000";
var TOTAL_ERR = "the total votes must be above 0";
var SEATS_ERR = "the seats must be a whole number from 1 to 1000";

function _votes(t) {
  t = typeof t === "string" ? t.trim() : "";
  var parts = t.split(",").map(function (x) { return x.trim(); });
  if (parts.length < 1 || parts.length > 8) throw new Error(VOTES_ERR);
  var v = parts.map(function (x) {
    if (!/^[0-9]{1,10}$/.test(x)) throw new Error(VOTES_ERR);
    var n = BigInt(x);
    if (n > 1000000000n) throw new Error(VOTES_ERR);
    return n;
  });
  return v;
}
function _seats(t) {
  t = typeof t === "string" ? t.trim() : "";
  if (!/^[0-9]{1,6}$/.test(t)) throw new Error(SEATS_ERR);
  var n = parseInt(t, 10);
  if (n < 1 || n > 1000) throw new Error(SEATS_ERR);
  return n;
}
function _parse(votes, seats) {
  var v = _votes(votes);
  var s = _seats(seats);
  var total = v.reduce(function (a, b) { return a + b; }, 0n);
  if (total === 0n) throw new Error(TOTAL_ERR);
  return { v: v, s: s, total: total };
}
function _name(i) { return String.fromCharCode(65 + i); }
function _list(ix) {
  var n = ix.map(_name);
  if (n.length === 1) return n[0];
  return n.slice(0, -1).join(", ") + " and " + n[n.length - 1];
}
function _seatWord(n) { return n + (n === 1 ? " seat" : " seats"); }
function _render(label, s, counts, tieIdx, open, what) {
  var out = label + ", " + _seatWord(s) + ": " + counts.map(function (c, i) { return _name(i) + " " + c; }).join(", ") + ".";
  if (tieIdx.length) {
    out += " " + _seatWord(open) + (open === 1 ? " is" : " are") + " undecided because " + _list(tieIdx) + " tie (same " + what + ").";
  }
  return out;
}

// The remainder truth: the largest remainder method.
function remainderTruth(votes, seats) {
  var p = _parse(votes, seats), S = BigInt(p.s);
  var floors = p.v.map(function (x) { return (x * S) / p.total; });
  var rems = p.v.map(function (x) { return (x * S) % p.total; });
  var given = floors.reduce(function (a, b) { return a + b; }, 0n);
  var left = Number(S - given);
  var counts = floors.map(Number);
  if (left === 0) return _render("Largest remainder", p.s, counts, [], 0, "remainder");
  var order = rems.map(function (r, i) { return i; }).sort(function (a, b) { return rems[a] === rems[b] ? a - b : (rems[a] > rems[b] ? -1 : 1); });
  var cut = rems[order[left - 1]];
  var nextTie = left < order.length && rems[order[left]] === cut;
  var sure = order.filter(function (i) { return rems[i] > cut; });
  sure.forEach(function (i) { counts[i] += 1; });
  var tied = order.filter(function (i) { return rems[i] === cut; });
  if (!nextTie) {
    tied.slice(0, left - sure.length).forEach(function (i) { counts[i] += 1; });
    return _render("Largest remainder", p.s, counts, [], 0, "remainder");
  }
  tied.sort(function (a, b) { return a - b; });
  return _render("Largest remainder", p.s, counts, tied, left - sure.length, "remainder");
}

function _averages(label, votes, seats, step) {
  var p = _parse(votes, seats);
  var items = [];
  p.v.forEach(function (x, i) {
    if (x === 0n) return;
    for (var j = 0; j < p.s; j++) items.push({ v: x, d: BigInt(step(j)), i: i });
  });
  items.sort(function (a, b) {
    var l = a.v * b.d, r = b.v * a.d;
    if (l !== r) return l > r ? -1 : 1;
    return a.i - b.i;
  });
  var cut = items[p.s - 1];
  var same = function (a, b) { return a.v * b.d === b.v * a.d; };
  var gt = function (a, b) { return a.v * b.d > b.v * a.d; };
  var counts = p.v.map(function () { return 0; });
  var k = 0;
  items.forEach(function (it) { if (gt(it, cut)) { counts[it.i] += 1; k++; } });
  var tied = items.filter(function (it) { return same(it, cut); }).map(function (it) { return it.i; });
  var room = p.s - k;
  if (tied.length <= room) {
    tied.forEach(function (i) { counts[i] += 1; });
    return _render(label, p.s, counts, [], 0, "quotient");
  }
  tied.sort(function (a, b) { return a - b; });
  return _render(label, p.s, counts, tied, room, "quotient");
}

// The highest averages methods.
function dhondtTruth(votes, seats) { return _averages("D'Hondt", votes, seats, function (j) { return j + 1; }); }
function laguTruth(votes, seats) { return _averages("Sainte-Lague", votes, seats, function (j) { return 2 * j + 1; }); }
