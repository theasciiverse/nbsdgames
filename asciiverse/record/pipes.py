"""Records asciiverse/casts/pipes.cast: the fixed 20x14 board. The driver
reads the next pipe off the queue on the left and lays it at the end of the
pipeline when it fits there and leaves room to grow; pipes that do not fit
go on three scrap rows along the far edge. After a while it starts the flow
with g, keeps building, then turns on fast flow with f so the sewage races
through the pipeline to its end, and leaves at the high scores with n."""
from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

W, H = 20, 14
SX = 7
BUILD, GO, FAST = 26, 33, 50
N, E, S, Wd = 1, 2, 4, 8          # UP RIGHT DOWN LEFT, as in pipes.c
STEP = {N: (-1, 0), E: (0, 1), S: (1, 0), Wd: (0, -1)}
OPP = {N: S, S: N, E: Wd, Wd: E}
GLYPH = {"m": N | E, "x": N | S, "j": N | Wd, "l": S | E, "k": S | Wd, "q": E | Wd, "n": 15,
         ">": E, "<": Wd, "^": N, "v": S}

r = Rec("pipes", "Pipes")
r.wait_for("IPES")
r.pump(1.5)
cy = cx = 0


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.03); cy += 1
    while cy > y: r.key(UP, 0.03); cy -= 1
    while cx < x: r.key(RIGHT, 0.03); cx += 1
    while cx > x: r.key(LEFT, 0.03); cx -= 1


def cell(y, x):
    return r.grid()[1 + y][SX + 1 + x]


def next_pipe():
    return GLYPH.get(r.grid()[11][4], 0)


# the source: the one arrow on the board
src = next((y, x) for y in range(H) for x in range(W) if cell(y, x) in "<>^v")
d = GLYPH[cell(*src)]
head = (src[0] + STEP[d][0], src[1] + STEP[d][1])
entry = OPP[d]                     # the side the sewage comes in by
used = {src}
# scrap cells: the three edge rows farthest from the source
scrap_rows = (0, 1, 2) if src[0] > H // 2 else (H - 1, H - 2, H - 3)
scrap = [(y, x) for y in scrap_rows for x in range(W)]
used |= set(scrap)
filled_scrap = set()


def free(y, x):
    return 0 <= y < H and 0 <= x < W and (y, x) not in used


def room(y, x, head):
    """How many open cells the pipeline could still grow into from (y, x)."""
    seen, todo = {(y, x), head}, [(y, x)]
    for a, b in todo:
        for dy, dx in STEP.values():
            n = (a + dy, b + dx)
            if n not in seen and free(*n):
                seen.add(n)
                todo.append(n)
    return len(todo)


def lay(p):
    """Where pipe p would lead if laid at the head, or None if it does not fit."""
    global head, entry
    if not (p & entry):
        return None
    out = entry ^ 15 if p == 15 else p & ~entry
    if out not in STEP:
        return None
    ny, nx = head[0] + STEP[out][0], head[1] + STEP[out][1]
    if not free(ny, nx):
        return None
    return out, (ny, nx)


def place():
    global head, entry
    p = next_pipe()
    if not p:
        r.pump(0.2)
        return
    fit = lay(p) if free(*head) else None
    if fit and room(*fit[1], head) >= 25:
        out, nxt = fit
        go(*head)
        r.key(ENTER, 0.15)
        used.add(head)
        head, entry = nxt, OPP[out]
    else:
        # the nearest empty scrap cell; once they are all taken, replace
        # one (which costs a point)
        spots = [c for c in scrap if c not in filled_scrap] or scrap
        y, x = min(spots, key=lambda c: abs(c[0] - cy) + abs(c[1] - cx))
        filled_scrap.add((y, x))
        go(y, x)
        r.key(ENTER, 0.15)


while r.elapsed() < BUILD:
    place()
r.key("g", 0.3)
while r.elapsed() < GO:
    place()
r.pump(1.0)
r.key("f", 0.2)
while "Game over" not in r.text() and r.elapsed() < FAST:
    r.pump(0.2)
r.pump(2.5)
r.key("x", 2.5)                    # on to the high scores
r.finish(b"n")
