"""Records asciiverse/casts/fifteen.cast: the classic 4x4 board. The driver
reads the shuffled tiles off the screen, finds a solution with a weighted A*
search on the Manhattan distance, and plays it with the cursor and Enter,
sliding a whole row or column of tiles in one go where the solution moves
several the same way. A solved board is played again with y while there is
time."""
import heapq

from rec import Rec, UP, DOWN, LEFT, RIGHT, ENTER

N = 4
SECONDS = 42
SIGNS = "123456789abcdefghijklmnopqrstuvwxyz"
GOAL = tuple(list(range(1, N * N)) + [0])

r = Rec("fifteen", "Fifteen")
r.wait_for("IFTEEN")
r.pump(1.5)
cy = cx = 0


def board():
    rows = r.grid()
    cells = []
    for y in range(N):
        for x in range(N):
            c = rows[4 + y][1 + 2 * x]
            cells.append(0 if c == " " else SIGNS.index(c) + 1)
    return tuple(cells)


def h(state):
    d = 0
    for i, t in enumerate(state):
        if t:
            g = t - 1
            d += abs(i // N - g // N) + abs(i % N - g % N)
    return d


def solve(start):
    """A list of blank positions, one per move (weighted A*, w = 2)."""
    frontier = [(2 * h(start), 0, start, start.index(0))]
    back = {start: None}
    while frontier:
        _, g, s, b = heapq.heappop(frontier)
        if s == GOAL:
            path = []
            while back[s]:
                s, b2 = back[s]
                path.append(b2)
            return path[::-1]
        y, x = divmod(b, N)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < N and 0 <= nx < N:
                nb = ny * N + nx
                t = list(s)
                t[b], t[nb] = t[nb], 0
                t = tuple(t)
                if t not in back:
                    back[t] = (s, nb)
                    heapq.heappush(frontier, (g + 1 + 2 * h(t), g + 1, t, nb))


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.07); cy += 1
    while cy > y: r.key(UP, 0.07); cy -= 1
    while cx < x: r.key(RIGHT, 0.07); cx += 1
    while cx > x: r.key(LEFT, 0.07); cx -= 1


def play(path, blank):
    """Click the tile the blank moves to; runs in one line become one click."""
    i = 0
    while i < len(path) and r.elapsed() < SECONDS:
        step = path[i] - blank
        j = i
        while j + 1 < len(path) and path[j + 1] - path[j] == step:
            j += 1
        target = path[j]
        go(*divmod(target, N))
        r.key(ENTER, 0.22)
        blank = target
        i = j + 1


while r.elapsed() < SECONDS:
    start = board()
    play(solve(start), start.index(0))
    if "solved" in r.text():
        r.pump(2.5)
        if r.elapsed() > SECONDS - 15:
            break
        r.key("y", 1.0)
        cy = cx = 0
r.pump(1.0)
r.finish(b"n" if "solved" in r.text() else b"q")
