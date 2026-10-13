"""Records asciiverse/casts/jewels.cast: a planning driver reads the
well off the screen and, for each falling pair, tries every column and
all four turns, drops each one in a copy of the well with the game's own
rules (four or more in a row explode, the rest falls, chains score
more), and plays the placement that scores most or sets up the most
matching neighbours while keeping the middle low. It turns the pair
with k, moves it with j and l, and drops it with space; q quits."""
import random

from rec import Rec

SECONDS = 50
LEN, WID = 17, 19
LEFT0 = 16                                # first column of the well (MIDDLE in src/jewels.c)
r = Rec("jewels", "Jewels")
r.wait_for("Score")
r.pump(0.6)


def well():
    rows = r.grid()
    return [[rows[y][LEFT0 + x] for x in range(WID)] for y in range(LEN)]


def loose(b):
    """Cells with an empty cell somewhere below: the falling pair."""
    out = []
    for x in range(WID):
        gap = False
        for y in range(LEN - 1, -1, -1):
            if b[y][x] == " ":
                gap = True
            elif gap:
                out.append((y, x))
    return out


def settle(b):
    for x in range(WID):
        col = [b[y][x] for y in range(LEN) if b[y][x] != " "]
        col = [" "] * (LEN - len(col)) + col
        for y in range(LEN):
            b[y][x] = col[y]


def explode(b, combo):
    """The game's explode(): rows first, then columns, runs of four or more."""
    pts = 0
    for y in range(LEN):
        x = 0
        while x < WID:
            e = x
            while e < WID and b[y][x] != " " and b[y][e] == b[y][x]:
                e += 1
            n = e - x
            if n >= 4:
                pts += (n - 1) * 10 * (n - 3) * combo
                for i in range(x, e):
                    b[y][i] = " "
            x = max(e, x + 1)
    for x in range(WID):
        y = 0
        while y < LEN:
            e = y
            while e < LEN and b[y][x] != " " and b[e][x] == b[y][x]:
                e += 1
            n = e - y
            if n >= 4:
                pts += (n - 1) * 10 * (n - 3) * combo
                for i in range(y, e):
                    b[i][x] = " "
            y = max(e, y + 1)
    return pts


def height(b, x):
    return next((LEN - y for y in range(LEN) if b[y][x] != " "), 0)


def drop(b, cells):
    """Place (column, char) pairs, bottom one first, and settle."""
    for x, c in cells:
        y = LEN - 1 - height(b, x)
        if y < 0:
            return False
        b[y][x] = c
    return True


def value(b, first, second, rot, x):
    """Score putting the pair (left char `first`, right `second` at spawn) at
    turn `rot` with the pivot jewel (`second`) in column x."""
    nb = [row[:] for row in b]
    if rot == 0:   cells, cols = [(x - 1, first), (x, second)], (x - 1, x)
    elif rot == 2: cells, cols = [(x + 1, first), (x, second)], (x, x + 1)
    elif rot == 1: cells, cols = [(x, second), (x, first)], (x,)
    else:          cells, cols = [(x, first), (x, second)], (x,)
    if min(cols) < 0 or max(cols) >= WID or not drop(nb, cells):
        return None
    near = 0
    for cx in set(cols):
        y = LEN - height(nb, cx)
        c = nb[y][cx]
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            a, e = y + dy, cx + dx
            if 0 <= a < LEN and 0 <= e < WID and nb[a][e] == c:
                near += 1
    pts, combo = 0, 1
    while True:
        p = explode(nb, combo)
        if not p:
            break
        pts += p
        combo += 1
        settle(nb)
    mid = max(height(nb, WID // 2), height(nb, WID // 2 - 1))
    tall = max(height(nb, c) for c in range(WID))
    return pts * 10 + near * 6 - mid * 4 - tall - abs(x - WID // 2) * 0.3 + random.random()


def shape(b, pair):
    """('h', left, right) or ('v', top, bottom) for the loose pair, or None."""
    if len(pair) != 2:
        return None
    (y1, x1), (y2, x2) = sorted(pair, key=lambda p: (p[0], p[1]))
    if y1 == y2 and abs(x1 - x2) == 1:
        return ("h", b[y1][min(x1, x2)], b[y1][max(x1, x2)], min(x1, x2))
    if x1 == x2 and y2 - y1 == 1:
        return ("v", b[y1][x1], b[y2][x1], x1)
    return None


while r.elapsed() < SECONDS:
    r.pump(0.45)                           # let the new pair fall a row or two
    b = well()
    pair = loose(b)
    s = shape(b, pair)
    if not s or s[0] != "h":
        r.key(" ", 0.3)
        continue
    _, first, second, _ = s
    for y, x in pair:
        b[y][x] = " "
    best = max(((v, rot, x) for rot in range(4) for x in range(WID)
                if (v := value(b, first, second, rot, x)) is not None), default=None)
    if not best:
        r.key(" ", 0.3)
        continue
    _, rot, x = best
    want = {0: ("h", first, second, x - 1), 2: ("h", second, first, x),
            1: ("v", first, second, x), 3: ("v", second, first, x)}[rot]
    for _ in range(14):
        s = shape(well(), loose(well()))
        if not s:
            break
        if s[:3] != want[:3]:
            r.key("k", 0.09)
        elif s[3] < want[3]:
            r.key("l", 0.09)
        elif s[3] > want[3]:
            r.key("j", 0.09)
        else:
            break
    r.pump(0.12)
    r.key(" ", 0.3)
r.pump(1.0)
r.finish(b"q")
