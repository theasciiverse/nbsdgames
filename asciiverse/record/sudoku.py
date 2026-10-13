"""Records asciiverse/casts/sudoku.cast: the default 9x9 board, solved by a
driver that reads the given digits off the screen, works out a solution and
fills the cells the way a person would, the most constrained cell first.
When the board is full it starts a new one with y and fills part of it."""
from rec import Rec, UP, DOWN, LEFT, RIGHT

SECONDS = 48
r = Rec("sudoku", "Sudoku")
r.wait_for("UDOKU", 20)
r.pump(1.5)
cy = cx = 0


def board():
    """The 9x9 grid as digits, 0 for an empty cell."""
    rows = r.grid()
    g = []
    for y in range(9):
        line = rows[3 + y + y // 3 + 1]
        g.append([int(c) if c.isdigit() else 0 for c in (line[2 * x + 1] for x in range(9))])
    return g


def ok(g, y, x, v):
    if any(g[y][i] == v for i in range(9)) or any(g[i][x] == v for i in range(9)):
        return False
    by, bx = 3 * (y // 3), 3 * (x // 3)
    return all(g[by + a][bx + b] != v for a in range(3) for b in range(3))


def solve(g):
    best = None
    for y in range(9):
        for x in range(9):
            if not g[y][x]:
                c = [v for v in range(1, 10) if ok(g, y, x, v)]
                if best is None or len(c) < len(best[2]):
                    best = (y, x, c)
    if best is None:
        return True
    y, x, c = best
    for v in c:
        g[y][x] = v
        if solve(g):
            return True
    g[y][x] = 0
    return False


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.04); cy += 1
    while cy > y: r.key(UP, 0.04); cy -= 1
    while cx < x: r.key(RIGHT, 0.04); cx += 1
    while cx > x: r.key(LEFT, 0.04); cx -= 1


def play(until):
    """Fill the board, the cell with the fewest candidates first, nearest on ties."""
    g = board()
    sol = [row[:] for row in g]
    solve(sol)
    while r.elapsed() < until:
        cells = []
        for y in range(9):
            for x in range(9):
                if not g[y][x]:
                    n = sum(ok(g, y, x, v) for v in range(1, 10))
                    cells.append((n, abs(y - cy) + abs(x - cx), y, x))
        if not cells:
            return True
        _, _, y, x = min(cells)
        go(y, x)
        r.key(str(sol[y][x]), 0.3)
        g[y][x] = sol[y][x]
    return False


if play(SECONDS - 12):
    r.wait_for("play again", 3)
    r.pump(3.0)
    r.key("y", 0.5)
    r.wait_for("UDOKU", 20)
    r.pump(1.0)
    cy = cx = 0
    play(SECONDS)
r.pump(1.0)
r.finish(b"q")
