"""Records asciiverse/casts/memoblocks.cast: the 16x8 board of 64 pairs.
The driver plays with a memory: it remembers every glyph it has seen,
reveals the hidden tile nearest the cursor, and when that glyph's twin is
already known it goes straight to the twin to pair them. The full board
takes longer than a preview, so the cast ends partway through with q."""
from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

H, W = 8, 16
SECONDS = 45
r = Rec("memoblocks", "Memoblocks")
r.wait_for("EMORY")
r.pump(1.5)
cy = cx = 0


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.04); cy += 1
    while cy > y: r.key(UP, 0.04); cy -= 1
    while cx < x: r.key(RIGHT, 0.04); cx += 1
    while cx > x: r.key(LEFT, 0.04); cx -= 1


def tile(y, x):
    return r.grid()[4 + y][1 + x]


known = {}        # (y, x) -> glyph, for tiles seen but not yet paired
paired = set()


def reveal(y, x):
    go(y, x)
    r.key(ENTER, 0.25)
    return tile(y, x)


while r.elapsed() < SECONDS and "solved" not in r.text():
    hidden = [(y, x) for y in range(H) for x in range(W)
              if (y, x) not in known and (y, x) not in paired]
    if not hidden:
        break
    y, x = min(hidden, key=lambda c: (abs(c[0] - cy) + abs(c[1] - cx), c))
    g = reveal(y, x)
    twin = next((c for c, k in known.items() if k == g), None)
    if twin:
        r.pump(0.3)
        reveal(*twin)
        paired |= {twin, (y, x)}
        del known[twin]
    else:
        known[(y, x)] = g
r.pump(1.5)
r.finish(b"q")
