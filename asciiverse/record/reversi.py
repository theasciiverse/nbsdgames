"""Records asciiverse/casts/reversi.cast: the default setup, a human on
black (X) against the computer on white (O), answered at the two start-up
questions. The driver plays black with a plain positional heuristic:
corners first, then edges, avoiding the cells next to an empty corner,
and among equals the move that turns the most discs. When the game ends
it answers y and plays on until the time is up."""
from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

SECONDS = 50
r = Rec("reversi", "Reversi")
r.wait_for("white player", 5)
r.pump(0.8)
r.key("c", 0.8)              # white: computer
r.key("h", 0.8)              # black: human
r.wait_for("EVERSI")
r.pump(0.8)
cy = cx = 0
DIRS = [(dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
WEIGHT = [
    [100, -20, 10, 5, 5, 10, -20, 100],
    [-20, -40, -2, -2, -2, -2, -40, -20],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [5, -2, 1, 0, 0, 1, -2, 5],
    [10, -2, 1, 1, 1, 1, -2, 10],
    [-20, -40, -2, -2, -2, -2, -40, -20],
    [100, -20, 10, 5, 5, 10, -20, 100],
]


def board():
    rows = r.grid()
    return [[rows[4 + y][1 + 2 * x] for x in range(8)] for y in range(8)]


def flips(b, y, x, me):
    if b[y][x] != ".":
        return 0
    n = 0
    for dy, dx in DIRS:
        k, a, c = 0, y + dy, x + dx
        while 0 <= a < 8 and 0 <= c < 8 and b[a][c] not in (".", me):
            k, a, c = k + 1, a + dy, c + dx
        if k and 0 <= a < 8 and 0 <= c < 8 and b[a][c] == me:
            n += k
    return n


def choose(b):
    best = None
    for y in range(8):
        for x in range(8):
            n = flips(b, y, x, "X")
            if n:
                score = WEIGHT[y][x] * 10 + n
                if best is None or score > best[0]:
                    best = (score, y, x)
    return best and best[1:]


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.05); cy += 1
    while cy > y: r.key(UP, 0.05); cy -= 1
    while cx < x: r.key(RIGHT, 0.05); cx += 1
    while cx > x: r.key(LEFT, 0.05); cx -= 1


while r.elapsed() < SECONDS:
    if "again" in r.text():
        if r.elapsed() > SECONDS - 12:
            break
        r.pump(2.5)
        r.key("y", 0.8)
        cy = cx = 0
        continue
    move = choose(board())
    if not move:
        r.pump(0.3)
        continue
    go(*move)
    r.pump(0.2)
    r.key(ENTER, 0.7)
r.pump(1.5)
r.finish(b"n" if "again" in r.text() else b"qn")
