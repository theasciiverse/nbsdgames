"""Records asciiverse/casts/sjump.cast. The O runs clockwise round the
border of its square; Enter sends it flying, in the direction it sits from
the square's middle, and it has to land in the next square. The driver
finds both squares and the O on the screen, works out with the game's own
flight rules which border cells land, and presses Enter two cells ahead
of them. Late in the cast it jumps badly on purpose once, so the high scores
show, then plays again and ends with q."""
import math


from rec import Rec, ENTER

SIZE = 12
LEN = 24
SECONDS = 45
r = Rec("sjump", "Square Jump")
r.wait_for("UMP")
r.pump(1.0)


def cround(v):
    return math.floor(v + 0.5) if v >= 0 else -math.floor(-v + 0.5)


def squares():
    """Top-left corners of the squares on screen, found by any visible corner."""
    rows = r.grid()
    found = set()
    for y in range(3, len(rows)):
        for x, ch in enumerate(rows[y]):
            near = rows[y][x - 1:x + 2]
            if "q" not in near:
                continue
            if ch == "l": found.add((y, x))
            elif ch == "k": found.add((y, x - 2 * SIZE))
            elif ch == "m": found.add((y - SIZE, x))
            elif ch == "j": found.add((y - SIZE, x - 2 * SIZE))
    return sorted(found, key=lambda s: s[1])


def the_o():
    rows = r.grid()
    for y in range(3, len(rows)):
        x = rows[y].find("O")
        if x >= 0:
            return y, x
    return None


def perimeter():
    """Border cells of a square in the order the O visits them (clockwise)."""
    cells = [(0, x) for x in range(2 * SIZE)]
    cells += [(y, 2 * SIZE) for y in range(SIZE)]
    cells += [(SIZE, x) for x in range(2 * SIZE, 0, -1)]
    cells += [(y, 0) for y in range(SIZE, 0, -1)]
    return cells


RING = perimeter()


def shot(sq0, sq1, oy, ox):
    """0 for a miss, 1 for a landing, 2 for a landing on a top or bottom edge."""
    dy = (oy - SIZE // 2) / SIZE / 2
    dx = (ox - SIZE) / (SIZE * 2)
    y, x = sq0[0] + oy, sq0[1] + ox
    for _ in range(2000):
        y += dy
        x += dx
        if y >= LEN - 1 or y <= 1 or x > sq1[1] + SIZE * 3 or x < -SIZE:
            return 0
        if y >= sq1[0] and x >= sq1[1] and y <= sq1[0] + SIZE and cround(x) <= sq1[1] + 2 * SIZE:
            return 2 if cround(y) in (sq1[0], sq1[0] + SIZE) else 1
    return 0


def jump(want_miss=False):
    """Wait for a good cell to come round, then press Enter just before it."""
    deadline = r.elapsed() + 6
    while r.elapsed() < deadline:
        sq = squares()
        o = the_o()
        if len(sq) < 2 or not o:
            r.pump(0.03)
            continue
        sq0, sq1 = sq[0], sq[1]
        rel = (o[0] - sq0[0], o[1] - sq0[1])
        if rel not in RING:
            r.pump(0.03)
            continue
        i = RING.index(rel)
        # the key is read on the game's next turn, and the O has moved
        # one more cell by the time it flies: aim two cells ahead
        ahead = [shot(sq0, sq1, *RING[(i + k) % len(RING)]) for k in (1, 2, 3)]
        if want_miss:
            ok = not any(ahead) and RING[i][1] < SIZE
        else:
            ok = ahead[1] and (ahead[0] or ahead[2])
        if ok:
            r.key(ENTER, 0.1)
            # the flight is drawn while the game ignores keys; wait it out
            r.pump(1.6)
            return
        r.pump(0.02)


def past_scores():
    if "Press a key to see" in r.text():
        r.pump(1.0)
        r.key(" ", 0.8)
    if "Press a key to proceed" in r.text():
        r.pump(2.0)
        r.key(" ", 0.8)


missed = False
while r.elapsed() < SECONDS:
    past_scores()
    if "play again" in r.text():
        r.pump(2.0)
        r.key("y", 0.8)
        continue
    miss = not missed and r.elapsed() > 30
    jump(want_miss=miss)
    missed = missed or miss
r.key("q", 0.8)
past_scores()
r.wait_for("play again", 3)
r.pump(1.5)
r.finish(b"n")
