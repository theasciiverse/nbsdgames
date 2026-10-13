"""Records asciiverse/casts/miketron.cast: the default board for a 100x30
terminal (80x23), played by a driver that reads the board off the screen.
Each frame it turns toward whichever free way leaves the most room, and
among equally roomy ways toward the nearest pick-up; a stop (S) is left
with the next key. A lost game is restarted with y."""
from collections import deque


from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER


SECONDS = 45
KEYS = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
STEP = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
BACK = {"U": "D", "D": "U", "L": "R", "R": "L"}
ITEMS = set("?&%8B")
ROOM = 250        # flood fills stop counting here: enough room is enough
r = Rec("miketron", "Miketron")
r.wait_for("IKETRON")
r.pump(1.0)


def board():
    """(cells, styled): the board characters (the trail and the vehicle are
    'n', curses' plus sign) and the board cells drawn bold, reversed or in
    color, which is where the vehicle is."""
    rows = r.grid()
    buf = r.cells()
    top = next((i for i, l in enumerate(rows) if l.startswith("lq")), None)
    if top is None:
        return None, None
    bottom = next((i for i in range(top + 1, len(rows)) if rows[i].startswith("mq")), None)
    if bottom is None or "k" not in rows[top]:
        return None, None
    wid = rows[top].rindex("k") - 1
    cells, styled = [], []
    for y in range(top + 1, bottom):
        line = buf[y]
        cells.append(rows[y][1:1 + wid])
        for x in range(wid):
            c = line[x + 1]
            if c.data == "n" and (c.reverse or c.bold or c.fg != "default"):
                styled.append((y - top - 1, x))
    return cells, styled


def wrap(cells, y, x):
    return y % len(cells), x % len(cells[0])


def room(cells, start, blocked):
    """How many cells can be reached from start, up to ROOM."""
    seen = {start}
    q = deque([start])
    while q and len(seen) < ROOM:
        y, x = q.popleft()
        for dy, dx in STEP.values():
            n = wrap(cells, y + dy, x + dx)
            if n not in seen and n not in blocked and cells[n[0]][n[1]] != "n":
                seen.add(n)
                q.append(n)
    return len(seen)


def item_distance(cells, blocked):
    """Distance from every free cell to the nearest pick-up."""
    dist = {}
    q = deque()
    for y, line in enumerate(cells):
        for x, ch in enumerate(line):
            if ch in ITEMS:
                dist[(y, x)] = 0
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for dy, dx in STEP.values():
            n = wrap(cells, y + dy, x + dx)
            if n not in dist and n not in blocked and cells[n[0]][n[1]] != "n":
                dist[n] = dist[(y, x)] + 1
                q.append(n)
    return dist


def choose(cells, me, heading):
    blocked = {me}
    dist = item_distance(cells, blocked)
    best, best_score = heading, None
    for d, (dy, dx) in STEP.items():
        if heading and d == BACK[heading]:
            continue
        n = wrap(cells, me[0] + dy, me[1] + dx)
        if cells[n[0]][n[1]] == "n":
            continue
        score = room(cells, n, blocked) * 100 - 4 * dist.get(n, 99) + (2 if d == heading else 0)
        if best_score is None or score > best_score:
            best, best_score = d, score
    return best


heading, me, last_change, last_text = "L", None, 0.0, ""
while r.elapsed() < SECONDS:
    text = r.text()
    if "Press a key to see the high scores" in text or "Press a key to proceed" in text:
        r.pump(2.0)          # let the end of the game be seen
        r.key(ENTER, 1.0)
        continue
    if "Wanna play again" in text:
        r.pump(1.5)
        r.key("y", 0.8)
        heading, me = "L", None
        continue
    if text != last_text:
        last_text, last_change = text, r.elapsed()
    elif r.elapsed() - last_change > 0.5:
        # an S stops the vehicle until a key is pressed
        r.key(KEYS[heading], 0.05)
        last_change = r.elapsed()
        continue
    cells, styled = board()
    if not cells:
        r.pump(0.03)
        continue
    if len(styled) == 1:
        me = styled[0]
    elif me is not None:
        # no trail behind it now: the vehicle is the plus sign next to where it was
        ahead = wrap(cells, me[0] + STEP[heading][0], me[1] + STEP[heading][1])
        me = ahead if cells[ahead[0]][ahead[1]] == "n" else me
    if me is None:
        r.pump(0.03)
        continue
    d = choose(cells, me, heading)
    if d != heading:
        r.key(KEYS[d], 0.03)
        heading = d
    else:
        r.pump(0.03)
r.pump(1.0)
r.finish(b"q")
