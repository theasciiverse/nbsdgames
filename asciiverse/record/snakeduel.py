"""Records asciiverse/casts/snakeduel.cast: the default board for a 100x30
terminal (95x23), the player's snake driven against the computer's by a
driver that reads the board off the screen. Each frame it takes the way
that leaves it the most cells it can reach before the computer's snake,
the usual light-cycle rule of thumb. Each round is followed by the next
with y."""
from collections import deque


from rec import Rec, UP, DOWN, LEFT, RIGHT


SECONDS = 45
KEYS = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
DEPTH = 6
STEP = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}
BACK = {"U": "D", "D": "U", "L": "R", "R": "L"}
r = Rec("snakeduel", "Snakeduel")
r.wait_for("UEL")


def board():
    """(h, w, cells): cells maps (y, x) to the color of the snake there."""
    rows = r.grid()
    buf = r.cells()
    top = next((i for i, l in enumerate(rows) if l.startswith("lq")), None)
    if top is None or "k" not in rows[top]:
        return None
    bottom = next((i for i in range(top + 1, len(rows)) if rows[i].startswith("mq")), None)
    if bottom is None:
        return None
    w = rows[top].rindex("k") - 1
    cells = {}
    for y in range(top + 1, bottom):
        line = buf[y]
        for x in range(w):
            c = line[x + 1]
            if c.reverse:
                cells[(y - top - 1, x)] = c.fg
    return bottom - top - 1, w, cells


def head(old_head, new_cells):
    """Follows the snake's new cells from where its head was."""
    y, x = old_head
    seen = {old_head}
    while True:
        nxt = [(y + dy, x + dx) for dy, dx in STEP.values()
               if (y + dy, x + dx) in new_cells and (y + dy, x + dx) not in seen]
        if not nxt:
            return (y, x)
        y, x = nxt[0]
        seen.add((y, x))


def distances(h, w, start, blocked):
    """Steps from start to every cell it can reach."""
    dist = {start: 0}
    q = deque([start])
    while q:
        y, x = q.popleft()
        for dy, dx in STEP.values():
            n = (y + dy, x + dx)
            if 0 <= n[0] < h and 0 <= n[1] < w and n not in dist and n not in blocked:
                dist[n] = dist[(y, x)] + 1
                q.append(n)
    return dist


def choose(h, w, cells, me, heading, enemy):
    """Tries each way a few cells deep and takes the one after which the
    player reaches the most cells before the computer's snake can, keeping
    clear of that snake's head and close to the walls."""
    blocked = set(cells) | {me}

    def free(c, extra=()):
        return 0 <= c[0] < h and 0 <= c[1] < w and c not in blocked and c not in extra

    best, best_score = heading, None
    for d, (dy, dx) in STEP.items():
        if d == BACK[heading]:
            continue
        # a snake moves two cells a frame, and the screen read may be a frame old
        path = []
        for k in range(1, DEPTH + 1):
            c = (me[0] + dy * k, me[1] + dx * k)
            if not free(c):
                break
            path.append(c)
        if not path:
            continue
        end = path[-1]
        trail = set(path[:-1])
        mine = distances(h, w, end, blocked | trail)
        theirs = distances(h, w, enemy, (blocked | trail | {end}) - {enemy}) if enemy else {}
        owned = sum(1 for c, k in mine.items() if k + len(path) < theirs.get(c, 10 ** 6))
        n = path[0]
        near = enemy and abs(n[0] - enemy[0]) + abs(n[1] - enemy[1]) <= 3
        # hugging walls and trails fills a closed-off area without leaving holes
        hug = sum(1 for ey, ex in STEP.values() if not free((n[0] + ey, n[1] + ex)))
        score = (owned * 10 - (3000 if near else 0) - (100000 if len(path) < 2 else 0)
                 - (2000 if len(path) < 4 else 0) + hug * 4 + (5 if d == heading else 0))
        if best_score is None or score > best_score:
            best, best_score = d, score
    return best


def new_round():
    return {"mine": None, "mine_head": None, "enemy_head": None,
            "known": set(), "heading": "U"}


s = new_round()
while r.elapsed() < SECONDS:
    if "Wanna play again" in r.text():
        r.pump(1.5)          # let the crash be seen
        r.key("y", 0.5)
        s = new_round()
        continue
    b = board()
    if not b:
        r.pump(0.02)
        continue
    h, w, cells = b
    if cells.keys() == s["known"]:
        r.pump(0.01)
        continue
    new = {p: c for p, c in cells.items() if p not in s["known"]}
    s["known"] = set(cells)
    if s["mine"] is None:
        # both snakes start in the middle going up; the player's is the right one
        colors = {}
        for (y, x), c in cells.items():
            colors.setdefault(c, []).append((y, x))
        if len(colors) < 2:
            s["known"] = set()
            r.pump(0.02)
            continue
        s["mine"] = max(colors, key=lambda c: max(x for _, x in colors[c]))
        enemy_color = next(c for c in colors if c != s["mine"])
        s["mine_head"] = min(colors[s["mine"]])
        s["enemy_head"] = min(colors[enemy_color])
    else:
        mine_new = {p for p, c in new.items() if c == s["mine"]}
        enemy_new = {p for p, c in new.items() if c != s["mine"]}
        if mine_new:
            s["mine_head"] = head(s["mine_head"], mine_new)
        if enemy_new:
            s["enemy_head"] = head(s["enemy_head"], enemy_new)
    d = choose(h, w, cells, s["mine_head"], s["heading"], s["enemy_head"])
    if d != s["heading"]:
        r.key(KEYS[d], 0.0)
        s["heading"] = d
r.pump(1.0)
r.finish(b"q")
