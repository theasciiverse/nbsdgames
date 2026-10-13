"""Records asciiverse/casts/revenge.cast. You are the rat (r) in a field of
blocks (#) with cats (f) closing in; moving pushes whole rows of blocks,
and a cat that cannot move turns to cheese (%). The driver reads the field
off the screen and searches a few moves ahead with the game's own push
rule, letting the cats step toward the rat at each tick of the clock: it
keeps clear of them and pushes blocks so they have as few free cells as
possible. When a cat gets the rat the scores
show and a new game starts; it ends with q."""
import random, time


from rec import Rec, UP, DOWN, LEFT, RIGHT

N = 20
SECONDS = 48
r = Rec("revenge", "Revenge")
r.wait_for("EVENGE")
r.pump(1.0)

MOVES = {UP: (-1, 0), DOWN: (1, 0), LEFT: (0, -1), RIGHT: (0, 1),
         "y": (-1, -1), "u": (-1, 1), "b": (1, -1), "n": (1, 1)}


def field():
    """The field as lists of ' ', '#', 'f', '%', and the rat's position."""
    rows = r.grid()
    b, rat = [], None
    for y in range(N):
        line = rows[4 + y]
        row = []
        for x in range(N):
            c = line[1 + 2 * x] if len(line) > 1 + 2 * x else " "
            if c == "r":
                rat = (y, x)
                c = " "
            row.append(c if c in "#f%" else " ")
        b.append(row)
    return b, rat


def push(b, rat, dy, dx):
    """The game's tile_push: a new field and rat, or None if it cannot move."""
    y, x = rat[0] + dy, rat[1] + dx
    while 0 <= y < N and 0 <= x < N:
        c = b[y][x]
        if c in " %":
            nb = [row[:] for row in b]
            nb[y][x] = "#"
            nb[rat[0] + dy][rat[1] + dx] = " "
            return nb, (rat[0] + dy, rat[1] + dx)
        if c != "#":
            return None
        y += dy
        x += dx
    return None


def cats_of(b):
    return [(y, x) for y in range(N) for x in range(N) if b[y][x] == "f"]


def free_around(b, y, x):
    n = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            a, c = y + dy, x + dx
            if (dy or dx) and 0 <= a < N and 0 <= c < N and b[a][c] == " ":
                n += 1
    return n


def cats_move(b, rat):
    """The cats' first choices: straight at the rat, then along one axis."""
    nb = [row[:] for row in b]
    dead = False
    for y, x in cats_of(b):
        dy = (rat[0] > y) - (rat[0] < y)
        dx = (rat[1] > x) - (rat[1] < x)
        for a, c in ((dy, dx), (0, dx), (dy, 0)):
            ny, nx = y + a, x + c
            if (a or c) and 0 <= ny < N and 0 <= nx < N and nb[ny][nx] == " ":
                nb[y][x] = " "
                nb[ny][nx] = "f"
                if (ny, nx) == rat:
                    dead = True
                break
    return nb, dead


def score(b, rat):
    cats = cats_of(b)
    s = 0.0
    for cy, cx in cats:
        if max(abs(cy - rat[0]), abs(cx - rat[1])) <= 1:
            s -= 200
        free = free_around(b, cy, cx)
        s -= 10 * free + (30 if free else 0)
    if cats:
        near = min(max(abs(cy - rat[0]), abs(cx - rat[1])) for cy, cx in cats)
        s -= abs(near - 2)
    return s


def choose(b, rat, last, left=3, depth=11, beam=40):
    """Beam search over the rat's next moves, with the cats stepping at
    the next tick of the clock; the first move of the best line."""
    lines = [(0.0, None, b, rat)]
    best = None
    for step in range(depth):
        nxt = []
        for _t, k, bb, rr in lines:
            for key, (dy, dx) in MOVES.items():
                q = push(bb, rr, dy, dx)
                if not q:
                    continue
                qb, qr = q
                if step + 1 == left or (step + 1 - left) % 5 == 0 and step + 1 > left:
                    qb, dead = cats_move(qb, qr)
                    if dead or any(max(abs(cy - qr[0]), abs(cx - qr[1])) <= 1 for cy, cx in cats_of(qb)) and step + 1 == depth:
                        continue
                s = score(qb, qr) + random.uniform(0, 1)
                if step == 0 and qr == last:
                    s -= 3
                nxt.append((s, k or key, qb, qr))
        if not nxt:
            break
        nxt.sort(key=lambda l: l[0], reverse=True)
        lines = nxt[:beam]
        if best is None or lines[0][0] > best[0]:
            best = lines[0]
    return best[1] if best else None


last = None
while r.elapsed() < SECONDS:
    t = r.text()
    if "Press a key to see" in t:
        r.pump(2.0)
        r.key(" ", 1.0)
        continue
    if "Press a key to proceed" in t:
        r.pump(2.0)
        r.key(" ", 1.0)
        continue
    if "play again" in t:
        r.pump(2.0)
        r.key("y", 1.0)
        last = None
        continue
    b, rat = field()
    if not rat:
        r.pump(0.1)
        continue
    # the cats step when the clock passes a whole second
    left = max(1, round((1 - time.time() % 1) / 0.2))
    k = choose(b, rat, last, left)
    last = rat
    if k is None:
        r.pump(0.2)
        continue
    r.key(k, random.uniform(0.16, 0.24))
r.pump(1.0)
r.finish(b"q")
