"""Records asciiverse/casts/trsr.cast: Treasure against the computer on the
default 15x15 field. You play Percent and move first; the computer plays
Square. The driver reads the field off the screen: where the numbers prove
a hidden cell holds treasure it opens that one, otherwise the cell most
likely to hold treasure next to a number, never one the numbers prove
empty, and a random hidden cell when nothing is known. It waits for the
computer to finish each turn, starts a new game when one is won, and ends
with q."""
import random


from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

N = 15
SECONDS = 48
r = Rec("trsr", "Treasure")
r.wait_for("player")
r.pump(0.8)
r.key(ENTER, 0.6)       # the first side, Percent: human (the default)
r.key(ENTER, 0.6)       # the second, Square: computer (the default)
r.wait_for("Turn")
r.pump(1.0)
cy = cx = 0


def board():
    """The field: '.' hidden, ' ' empty, digits, '%' or '#' found treasure."""
    rows = r.grid()
    top = next(i for i, l in enumerate(rows) if l.startswith("lq"))
    return [[rows[top + 1 + y][1 + 2 * x] for x in range(N)] for y in range(N)]


def around(y, x):
    return [(y + dy, x + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
            if (dy or dx) and 0 <= y + dy < N and 0 <= x + dx < N]


def pick(b):
    odds = {}
    safe = set()
    for y in range(N):
        for x in range(N):
            if not b[y][x].isdigit():
                continue
            near = around(y, x)
            hidden = [(a, c) for a, c in near if b[a][c] == "."]
            found = sum(1 for a, c in near if b[a][c] in "%#")
            if not hidden:
                continue
            left = int(b[y][x]) - found
            if left <= 0:
                safe.update(hidden)
                continue
            for cell in hidden:
                odds[cell] = max(odds.get(cell, 0), left / len(hidden))
    odds = {c: p for c, p in odds.items() if c not in safe}
    if odds:
        best = max(odds.values())
        return random.choice([c for c, p in odds.items() if p == best])
    hidden = [(y, x) for y in range(N) for x in range(N) if b[y][x] == "." and (y, x) not in safe]
    if not hidden:
        hidden = [(y, x) for y in range(N) for x in range(N) if b[y][x] == "."]
    return random.choice(hidden) if hidden else None


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.03); cy += 1
    while cy > y: r.key(UP, 0.03); cy -= 1
    while cx < x: r.key(RIGHT, 0.03); cx += 1
    while cx > x: r.key(LEFT, 0.03); cx -= 1


def my_turn():
    """True once Percent's turn has stayed on screen for a moment."""
    for _ in range(80):
        if "play again" in r.text():
            return False
        if "Percent's Turn" in r.text():
            r.pump(0.3)
            if "Percent's Turn" in r.text():
                return True
        r.pump(0.1)
    return False


while r.elapsed() < SECONDS:
    if "play again" in r.text():
        r.pump(2.5)          # let the result be seen
        r.key("y", 1.0)
        cy = cx = 0
        continue
    if not my_turn():
        continue
    cell = pick(board())
    if not cell:
        r.pump(0.5)
        continue
    go(*cell)
    r.pump(0.15)
    r.key(ENTER, 0.5)
r.pump(1.0)
r.finish(b"q")
