"""Records asciiverse/casts/checkers.cast: the default setup, a human on
black (the red pieces, moving up) against the computer on white,
answered at the two start-up questions. The driver plays black: it takes
the longest chain of jumps when it must jump, otherwise prefers a move
that crowns a man, then one that leaves the moved piece safe, and kings
close in on the nearest white piece. A game won early is replayed with y,
a later one ends the recording; if the time runs out first it resigns
with q. Either way it declines the rematch with n."""
import random

from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

SECONDS = 52
r = Rec("checkers", "Checkers")
r.wait_for("black player", 5)
r.pump(0.8)
r.key("h", 0.8)              # black: human
r.key("c", 0.8)              # white: computer
r.wait_for("HECKERS")
r.pump(0.8)
cy = cx = 0


def board():
    """8x8 of 0, -1/-2 for black (red) men/kings, 1/2 for white, as the game stores them."""
    buf = r.cells()
    b = []
    for y in range(8):
        row = []
        for x in range(8):
            c = buf[4 + y][1 + 2 * x]
            v = {"O": 1, "K": 2}.get(c.data, 0)
            row.append(-v if c.fg == "red" else v)
        b.append(row)
    return b


def inside(y, x):
    return 0 <= y < 8 and 0 <= x < 8


def dirs(v):
    """Diagonal steps a piece may take: men only forward, kings both ways."""
    ys = (-1, 1) if abs(v) == 2 else ((-1,) if v < 0 else (1,))
    return [(dy, dx) for dy in ys for dx in (-1, 1)]


def jumps_from(b, y, x):
    v = b[y][x]
    out = []
    for dy, dx in dirs(v):
        if inside(y + 2 * dy, x + 2 * dx) and b[y + dy][x + dx] * v < 0 and not b[y + 2 * dy][x + 2 * dx]:
            out.append((y + 2 * dy, x + 2 * dx))
    return out


def chain(b, y, x):
    """Longest jump chain from (y, x): (length, [squares])."""
    best = (0, [])
    for ty, tx in jumps_from(b, y, x):
        v = b[y][x]
        nb = [row[:] for row in b]
        nb[ty][tx], nb[y][x], nb[(y + ty) // 2][(x + tx) // 2] = v, 0, 0
        if ty == 0 and v == -1:
            n, path = 1, [(ty, tx)]
        else:
            n, path = chain(nb, ty, tx)
            n, path = n + 1, [(ty, tx)] + path
        if n > best[0]:
            best = (n, path)
    return best


def attacked(b, y, x):
    """Could a white piece jump the black piece at (y, x)?"""
    for dy in (-1, 1):
        for dx in (-1, 1):
            a, c = y + dy, x + dx           # the attacker
            ly, lx = y - dy, x - dx         # where it lands
            if inside(a, c) and inside(ly, lx) and b[a][c] > 0 and not b[ly][lx]:
                if b[a][c] == 2 or -dy == 1:
                    return True
    return False


def choose(b):
    mine = [(y, x) for y in range(8) for x in range(8) if b[y][x] < 0]
    jumps = [(chain(b, y, x), y, x) for y, x in mine if jumps_from(b, y, x)]
    if jumps:
        (n, path), y, x = max(jumps, key=lambda j: (j[0][0], random.random()))
        return y, x, path
    enemies = [(y, x) for y in range(8) for x in range(8) if b[y][x] > 0]
    moves = []
    for y, x in mine:
        v = b[y][x]
        for dy, dx in dirs(v):
            ty, tx = y + dy, x + dx
            if not inside(ty, tx) or b[ty][tx]:
                continue
            nb = [row[:] for row in b]
            nb[ty][tx], nb[y][x] = v, 0
            crown = ty == 0 and v == -1
            safe = not attacked(nb, ty, tx)
            hang = sum(attacked(nb, a, c) for a, c in mine if (a, c) != (y, x))
            near = 0
            if v == -2 and enemies:
                near = -min(max(abs(ty - a), abs(tx - c)) for a, c in enemies)
            moves.append((crown, safe, -hang, near, -ty * (v == -1), random.random(), y, x, [(ty, tx)]))
    if not moves:
        return None
    m = max(moves)
    return m[6], m[7], m[8]


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.05); cy += 1
    while cy > y: r.key(UP, 0.05); cy -= 1
    while cx < x: r.key(RIGHT, 0.05); cx += 1
    while cx > x: r.key(LEFT, 0.05); cx -= 1


while r.elapsed() < SECONDS:
    t = r.text()
    if "rematch" in t:
        if r.elapsed() > 30:
            break
        r.pump(2.5)
        r.key("y", 0.8)
        cy = cx = 0
        continue
    move = choose(board())
    if not move:
        r.pump(0.3)
        continue
    y, x, path = move
    for ty, tx in path:
        go(y, x)
        r.key(ENTER, 0.25)       # select the piece
        go(ty, tx)
        r.key(ENTER, 0.25)       # move it
        y, x = ty, tx
    r.pump(0.5)
if "rematch" in r.text():
    r.pump(2.5)
    r.finish(b"n")
else:
    r.key("q", 2.0)
    r.finish(b"n")
