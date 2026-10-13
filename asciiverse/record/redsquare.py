"""Records asciiverse/casts/redsquare.cast: the levels in order, played by a
driver that reads the board off the screen and moves the red square along
the shortest way to the X that keeps clear of live cells, and holds still
while the X is inside the square so it is caught. When the X is somewhere
the square cannot safely go, it waits nearby, a generation per key, for the
X to wander out. Each key moves the Game of Life on a generation. A lost
game is restarted with y."""
from collections import deque


from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER


SECONDS = 45
WID = 50
KEYS = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
STEP = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
r = Rec("redsquare", "Redsquare")
r.wait_for("QUARE")
r.pump(1.5)


def board():
    """(rows, square, cross) in screen terms: rows of the visible part of the
    board ('#' a live cell, 'O' a red one, 'S' the square), the square's top
    left corner and the X; either may be None."""
    rows = r.grid()
    buf = r.cells()
    top = next((i for i, l in enumerate(rows) if l[1:3] == "qq"), None)
    if top is None:
        return None, None, None
    bottom = next((i for i in range(top + 1, len(rows)) if rows[i].startswith("mq")), None)
    if bottom is None:
        return None, None, None
    cells, square, cross = [], None, None
    for y in range(top + 1, bottom):
        line = buf[y]
        row = ""
        for x in range(WID):
            c = line[x + 1]
            if c.data == " " and c.reverse:
                row += "S"
                if square is None:
                    square = (y - top - 1, x)
            elif c.data == "X":
                # drawn reversed over a live cell, red over a red one
                row += (("O" if c.fg == "red" else "#") if c.reverse else " ")
                cross = (y - top - 1, x)
            else:
                row += c.data
        cells.append(row)
    if square is not None and square[1] == 0 and cells[square[0]][WID - 1] == "S":
        square = (square[0], WID - 1)          # split across the side edge
    # the X drawn over the square's top left corner hides it
    if square and cross and cross[0] == square[0] and (square[1] - cross[1]) % WID == 1:
        square = cross
    return cells, square, cross


def apart(a, b):
    dx = abs(a[1] - b[1]) % WID
    return abs(a[0] - b[0]) + min(dx, WID - dx)


def life(alive, h):
    """One generation of Conway's Game of Life on the visible rows, wrapping
    at the sides like the game's board (rows out of view count as dead)."""
    counts = {}
    for y, x in alive:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    c = (y + dy, (x + dx) % WID)
                    counts[c] = counts.get(c, 0) + 1
    return {c for c, n in counts.items()
            if 0 <= c[0] < h and (n == 3 or (n == 2 and c in alive))}


def safe(after, h, y, x):
    """Whether a square moved to (y, x), with the board one generation on
    (after), has nothing around it, and still will a generation later: the
    game loses hold of a square that touches other cells."""
    sq = {(y + a, (x + b) % WID) for a in (0, 1) for b in (0, 1)}
    ring = {(y + a, (x + b) % WID) for a in (-1, 0, 1, 2) for b in (-1, 0, 1, 2)} - sq
    if ring & after:
        return False
    near = {(yy, xx % WID) for yy in range(y - 3, y + 5) for xx in range(x - 3, x + 5)}
    local = (after & near) | sq
    nxt = life(local, h)
    return sq <= nxt and not (ring & nxt)


def choose(cells, square, cross):
    """The first move of the shortest safe way to a square holding the X,
    or to the safe place nearest it. " " waits a generation in place (also
    when the X is out of view); None when there is no safe move at all."""
    h = len(cells)
    sq = {(square[0] + a, (square[1] + b) % WID) for a in (0, 1) for b in (0, 1)}
    alive = {(y, x) for y, row in enumerate(cells) for x, ch in enumerate(row) if ch in "#OS"}
    after = life(alive | sq, h) - sq    # a generation runs, then the square moves

    def ok(y, x):
        return 0 <= y < h - 1 and safe(after, h, y, x)

    if not cross:
        return " " if safe(after, h, *square) else None
    goals = {(cross[0] - a, (cross[1] - b) % WID) for a in (0, 1) for b in (0, 1)}

    def ways():
        first = {square: None}
        q = deque([square])
        while q:
            y, x = q.popleft()
            for d, (dy, dx) in STEP.items():
                n = (y + dy, (x + dx) % WID)
                if n not in first and ok(*n):
                    first[n] = ((y, x), d)
                    q.append(n)
        return first

    def first_step(first, p):
        while first[p][0] != square:
            p = first[p][0]
        return first[p][1]

    first = ways()
    best = min(first, key=lambda p: min(apart(p, g) for g in goals))
    if best == square:
        return " " if safe(after, h, *square) else None
    return first_step(first, best)


next_key = 0.0
while r.elapsed() < SECONDS:
    text = r.text()
    if "Wanna play again" in text:
        r.pump(1.0)
        r.key("y", 1.0)
        continue
    if "Press a key" in text:
        r.pump(2.0)          # let the result be seen
        r.key(ENTER, 0.8)
        continue
    if ">*>*>Top" in text:
        r.pump(1.0)
        r.key(ENTER, 0.6)
        continue
    if r.elapsed() < next_key:
        r.pump(0.03)
        continue
    cells, square, cross = board()
    if not cells or square is None:
        r.pump(0.1)          # no square now: wait for life to settle
        continue
    if sum(row.count("S") for row in cells) == 3:
        r.pump(0.1)          # the X is in the square: hold still
        continue
    d = choose(cells, square, cross)
    if d is None:
        r.pump(0.1)
        continue
    r.key(KEYS.get(d, d), 0.05)
    next_key = r.elapsed() + (0.12 if d == " " else 0.25)
r.pump(1.0)
r.finish(b"q")
