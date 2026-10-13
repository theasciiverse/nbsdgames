"""Records asciiverse/casts/mines.cast: a 30x16 field with 75 mines, played
by a small solver that reads the board off the screen. It opens the middle,
flags every cell the numbers prove is a mine, opens every cell they prove
safe, and guesses only when stuck; a lost game is restarted with y."""
import random

from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

W, H = 30, 16
SECONDS = 40
r = Rec("mines", "Mines", ["-w", str(W), "-l", str(H), "-m", "75"])
r.wait_for("INES")
r.pump(1.5)
cy = cx = 0


def board():
    """The field as a list of strings, '.' unopened, ' ' empty, digits, 'P' flagged."""
    rows = r.grid()
    top = next(i for i, l in enumerate(rows) if l.startswith("lq"))
    return [[rows[top + 1 + y][1 + 2 * x] for x in range(W)] for y in range(H)]


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.03); cy += 1
    while cy > y: r.key(UP, 0.03); cy -= 1
    while cx < x: r.key(RIGHT, 0.03); cx += 1
    while cx > x: r.key(LEFT, 0.03); cx -= 1


def around(y, x):
    return [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
            if (dy or dx) and 0 <= y + dy < H and 0 <= x + dx < W]


def step(b):
    """One deduction: ('flag' | 'open', y, x), or a guess."""
    for y in range(H):
        for x in range(W):
            if not b[y][x].isdigit():
                continue
            n = int(b[y][x])
            near = around(y, x)
            hidden = [(a, c) for a, c in near if b[a][c] == "."]
            flags = sum(1 for a, c in near if b[a][c] == "P")
            if hidden and n == flags + len(hidden):
                return ("flag", *hidden[0])
            if hidden and n == flags:
                return ("open", *hidden[0])
    hidden = [(y, x) for y in range(H) for x in range(W) if b[y][x] == "."]
    return ("open", *random.choice(hidden)) if hidden else None


go(H // 2, W // 2)
r.key(ENTER, 0.6)
while r.elapsed() < SECONDS:
    if "play again" in r.text():
        r.pump(2.5)          # let the revealed field be seen
        r.key("y", 1.0)
        cy = cx = 0
        go(H // 2, W // 2)
        r.key(ENTER, 0.6)
        continue
    move = step(board())
    if not move:
        r.pump(0.5)
        continue
    what, y, x = move
    go(y, x)
    r.key(" " if what == "flag" else ENTER, 0.12)
r.pump(1.0)
r.finish(b"q")
