"""Records asciiverse/casts/fisher.cast: the fixed 80x24 sea. Each tick the
driver reads the ten rows of sea life and the hook off the screen. It picks
the most valuable catch it can reach before that row's swimmer crosses the
line, provided nothing in the rows above will cross the line while the hook
is down and being reeled in, lowers the hook to meet it and reels the catch
up. When no catch is safe it keeps the hook near the surface. It quits with
q and leaves the high scores with n."""
from rec import Rec, UP, DOWN

SECONDS = 45
LINE, SEA = 40, 12           # the line's column and the first row of water
SYM = "~:=!@+><;&"           # what lives in each row, shallowest first
TICK = 0.12

r = Rec("fisher", "Fisher")
r.wait_for("ISHER")
r.pump(1.0)


def read():
    rows = r.grid()
    depth = 0
    while rows[SEA + depth][LINE] == "x":
        depth += 1
    caught = rows[SEA + depth][LINE] != ")"
    fish = []
    for n, s in enumerate(SYM):
        row = rows[SEA + 1 + n]
        at = [x for x, c in enumerate(row) if c == s]
        off = [x for x in at if x != LINE]
        fish.append((off or at or [None])[0])
    return depth, caught, fish


def arrival(n, x):
    """Ticks until swimmer n next reaches the line (even rows swim right)."""
    if x is None:
        return 999
    d = (LINE - x) % 80 if n % 2 == 0 else (x - LINE) % 80
    return d or 80


def plan(depth, fish):
    """The deepest catch that is safe to go for, or None."""
    for n in range(9, -1, -1):
        t = arrival(n, fish[n])
        down = n + 1 - depth
        if down > t:
            continue
        window = t + n + 1
        if all(arrival(k, fish[k]) > window for k in range(n)):
            return n
    return None


while r.elapsed() < SECONDS:
    if "again" in r.text():
        break
    depth, caught, fish = read()
    if caught:
        r.key(UP, TICK)
        continue
    target = plan(depth, fish)
    want = 0 if target is None else target + 1
    if depth < want:
        r.key(DOWN, TICK)
    elif depth > want:
        r.key(UP, TICK)
    else:
        r.pump(0.1)
r.pump(1.0)
if "again" not in r.text():
    r.key("q", 2.5)
r.finish(b"n")
