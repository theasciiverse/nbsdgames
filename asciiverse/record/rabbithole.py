"""Records asciiverse/casts/rabbithole.cast: at 100x30 the maze is 47x11
cells with 10 carrots. The maze is hidden until the rabbit walks it, so the
driver explores like a player: it remembers the openings the game shows in
each cell it has visited and heads for the unexplored opening nearest a
carrot, walking back through known passages to reach it. A finished maze is
played again with y while there is time, otherwise the cast ends with n."""
from rec import Rec, UP, DOWN, LEFT, RIGHT

SECONDS = 45
r = Rec("rabbithole", "Rabbithole")
r.wait_for("ABBITHOLE")
r.pump(1.5)

MOVES = {(-1, 0): UP, (1, 0): DOWN, (0, -1): LEFT, (0, 1): RIGHT}


def size():
    """The maze size rabbithole picks for the terminal (main() in rabbithole.c)."""
    return max(5, (r.screen.lines - 7) // 2), max(20, (r.screen.columns - 5) // 2)


def openings(y, x, H, W):
    """The passages out of cell (y, x): drawn as reverse-video gaps."""
    buf = r.cells()
    cy, cx = 4 + 2 * y, 1 + 2 * x
    out = []
    for (dy, dx) in MOVES:
        ny, nx = y + dy, x + dx
        if 0 <= ny < H and 0 <= nx < W and buf[cy + dy][cx + dx].reverse:
            out.append((dy, dx))
    return out


def rabbit(H, W):
    rows = r.grid()
    for y in range(H):
        for x in range(W):
            if rows[4 + 2 * y][1 + 2 * x] == "r":
                return (y, x)


def carrots(H, W):
    rows = r.grid()
    return [(y, x) for y in range(H) for x in range(W) if rows[4 + 2 * y][1 + 2 * x] == "%"]


def path_to(start, goal, links):
    """Shortest walk through cells already visited, as a list of steps."""
    back, todo = {start: None}, [start]
    for cell in todo:
        if cell == goal:
            break
        for d in links.get(cell, ()):
            n = (cell[0] + d[0], cell[1] + d[1])
            if n in links and n not in back:
                back[n] = (cell, d)
                todo.append(n)
    steps, cell = [], goal
    while back[cell]:
        cell, d = back[cell]
        steps.append(d)
    return steps[::-1]


def walk_cost(start, links):
    dist, todo = {start: 0}, [start]
    for cell in todo:
        for d in links.get(cell, ()):
            n = (cell[0] + d[0], cell[1] + d[1])
            if n in links and n not in dist:
                dist[n] = dist[cell] + 1
                todo.append(n)
    return dist


def play_maze():
    """Best-first exploration: of all the openings into unexplored maze, take
    the one with the shortest walk there plus distance on to a carrot."""
    H, W = size()
    links = {}
    while r.elapsed() < SECONDS and "again" not in r.text():
        pos = rabbit(H, W)
        if pos is None:
            r.pump(0.1)
            continue
        links[pos] = openings(*pos, H, W)
        goals = carrots(H, W) or [(H - 1, W - 1)]
        dist = walk_cost(pos, links)
        best = None
        for cell, ds in links.items():
            for d in ds:
                n = (cell[0] + d[0], cell[1] + d[1])
                if n in links or cell not in dist:
                    continue
                c = 0.25 * dist[cell] + min(abs(n[0] - a) + abs(n[1] - b) for a, b in goals)
                if best is None or c < best[0]:
                    best = (c, cell, d)
        if best is None:
            break
        _, cell, d = best
        for step in path_to(pos, cell, links) + [d]:
            r.key(MOVES[step], 0.05)


while r.elapsed() < SECONDS:
    play_maze()
    if "again" in r.text():
        r.pump(2.5)
        if r.elapsed() > SECONDS - 12:
            break
        r.key("y", 1.0)
r.pump(1.0)
r.finish(b"q" if "again" not in r.text() else b"n")
