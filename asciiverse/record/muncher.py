"""Records asciiverse/casts/muncher.cast: the default board for a 100x30
terminal (80x23), played by a driver that reads the board off the screen
and steers the muncher along the shortest path to the food around the
traps. A lost game is restarted with y."""
from collections import deque


from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER


SECONDS = 45
KEYS = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
STEP = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
r = Rec("muncher", "Muncher")
r.wait_for("UNCHER")
r.pump(1.0)


def board():
    """(cells, player): cells[y][x] is the board character, player is (y, x) or None."""
    rows = r.grid()
    top = next((i for i, l in enumerate(rows) if l.startswith("lq")), None)
    if top is None:
        return None, None
    bottom = next((i for i in range(top + 1, len(rows)) if rows[i].startswith("mq")), None)
    if bottom is None:
        return None, None
    wid = rows[top].rindex("k") - 1
    cells = [rows[y][1:1 + wid] for y in range(top + 1, bottom)]
    player = None
    for y, line in enumerate(cells):
        x = line.find("r")
        if x >= 0:
            player = (y, x)
    return cells, player


def first_step(cells, start):
    """The first move of a shortest path from start to any food, or None."""
    h, w = len(cells), len(cells[0])
    seen = {start: None}
    q = deque([start])
    while q:
        y, x = q.popleft()
        if cells[y][x] == "%" and (y, x) != start:
            while seen[(y, x)] and seen[(y, x)][0] != start:
                y, x = seen[(y, x)][0]
            return seen[(y, x)][1]
        for d, (dy, dx) in STEP.items():
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and (ny, nx) not in seen and cells[ny][nx] != "^":
                seen[(ny, nx)] = ((y, x), d)
                q.append((ny, nx))
    return None


def safe_step(cells, start, current):
    """With no path to food, any move that is not straight into a trap or a wall."""
    h, w = len(cells), len(cells[0])
    for d in [current] + list(STEP):
        if not d:
            continue
        ny, nx = start[0] + STEP[d][0], start[1] + STEP[d][1]
        if 0 <= ny < h and 0 <= nx < w and cells[ny][nx] != "^":
            return d
    return current


heading = None
while r.elapsed() < SECONDS:
    text = r.text()
    if "Press a key to see the high scores" in text or "Press a key to proceed" in text:
        r.pump(2.0)          # let the end of the game be seen
        r.key(ENTER, 1.0)
        continue
    if "Wanna play again" in text:
        r.pump(1.5)
        r.key("y", 0.8)
        heading = None
        continue
    cells, player = board()
    if not cells or not player:
        r.pump(0.03)
        continue
    d = first_step(cells, player) or safe_step(cells, player, heading)
    if d != heading:
        r.key(KEYS[d], 0.03)
        heading = d
    else:
        r.pump(0.03)
r.pump(1.0)
r.finish(b"q")
