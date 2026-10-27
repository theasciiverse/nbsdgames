"""Records asciiverse/casts/salvo.cast: single player against the
computer. The driver places its five ships at random spots with room
around them, turning a few of them with r, then shoots: on a checkerboard pattern while hunting,
around a hit until the ship is sunk, along the line once two hits line
up. It reads the "You have sunk my ..." message to know when a ship is
gone. A finished game is declined with n; if time runs out it quits with q."""
import random

from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

SECONDS = 56
LENGTHS = {"patrol boat": 2, "destroyer": 3, "battleship": 4, "carrier": 5, "submarine": 3}
r = Rec("salvo", "Salvo")
r.wait_for("Single Player", 5)
r.pump(1.0)
r.key("1", 0.8)
r.wait_for("Set your board")
r.pump(0.8)
cy = cx = 0


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.03); cy += 1
    while cy > y: r.key(UP, 0.03); cy -= 1
    while cx < x: r.key(RIGHT, 0.03); cx += 1
    while cx > x: r.key(LEFT, 0.03); cx -= 1


def own():
    """Cells of the left board that hold a ship."""
    rows = r.grid()
    return {(y, x) for y in range(10) for x in range(10) if rows[4 + y][1 + 2 * x] not in "~ "}


def spot(ships, n):
    """A random cell from which a ship of n fits in every direction without
    touching the others, so whichever way the game lays it, it stands alone."""
    def clear(y, x):
        return 0 <= y < 10 and 0 <= x < 10 and not any(
            (y + a, x + c) in ships for a in (-1, 0, 1) for c in (-1, 0, 1))
    cells = [(y, x) for y in range(10) for x in range(10)
             if all(clear(y + dy * i, x + dx * i) for dy, dx in ((0, -1), (-1, 0), (0, 1), (1, 0)) for i in range(n))]
    return random.choice(cells) if cells else (random.randrange(10), random.randrange(10))


# placing the fleet: patrol boat, destroyer, battleship, carrier, submarine
for n in (2, 3, 4, 5, 3):
    before = len(own())
    while True:
        go(*spot(own(), n))
        r.pump(0.15)
        r.key(ENTER, 0.3)
        if len(own()) > before:
            break
    for _ in range(random.choice((0, 0, 1, 2))):
        r.key("r", 0.35)
    r.key(ENTER, 0.4)

r.wait_for("ATTLESHIP")
r.pump(0.8)


def track():
    rows = r.grid()
    return [[rows[4 + y][23 + 2 * x] for x in range(10)] for y in range(10)]


dead = set()


def mark_sunk(b, y, x, n):
    """Mark the n hits of the ship just sunk at (y, x) as dead."""
    best = None
    for dy, dx in ((0, 1), (1, 0)):
        run = [(y, x)]
        for s in (1, -1):
            a, c = y + s * dy, x + s * dx
            while 0 <= a < 10 and 0 <= c < 10 and b[a][c] == "*" and (a, c) not in dead:
                run.append((a, c))
                a, c = a + s * dy, c + s * dx
        if len(run) >= n and (best is None or len(run) < len(best)):
            best = run
    for cell in (best or [(y, x)])[:n]:
        dead.add(cell)


def choose(b):
    live = [(y, x) for y in range(10) for x in range(10) if b[y][x] == "*" and (y, x) not in dead]
    free = lambda y, x: 0 <= y < 10 and 0 <= x < 10 and b[y][x] == "."
    for y, x in live:                         # extend a line of two hits
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            if (y + dy, x + dx) in live:
                a, c = y + dy, x + dx
                while (a, c) in live:
                    a, c = a + dy, c + dx
                if free(a, c):
                    return a, c
    for y, x in live:                         # around a single hit
        near = [(y + dy, x + dx) for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)) if free(y + dy, x + dx)]
        if near:
            return random.choice(near)
    cells = [(y, x) for y in range(10) for x in range(10) if b[y][x] == "." and (y + x) % 2 == 0]
    cells = cells or [(y, x) for y in range(10) for x in range(10) if b[y][x] == "."]
    return random.choice(cells)


while r.elapsed() < SECONDS:
    if "again" in r.text():
        break
    b = track()
    y, x = choose(b)
    cy, cx = 0, 0                             # every turn starts in the top left corner
    go(y, x)
    r.pump(0.15)
    r.key(ENTER, 0.45)
    line = r.grid()[15]
    for name, n in LENGTHS.items():
        if ("sunk my " + name) in line or (name == "destroyer" and "destroyed my destroyer" in line):
            mark_sunk(track(), y, x, n)
if "again" in r.text():
    r.pump(2.5)
    r.finish(b"n")
else:
    r.finish(b"q")
