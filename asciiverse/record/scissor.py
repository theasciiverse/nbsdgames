"""Records asciiverse/casts/scissor.cast. You are the highlighted scissor
among bouncing rocks (O), papers (#), scissors (>) and one magic item (?).
The driver finds itself and the others on the screen and steers, eight
ways, toward the nearest paper while keeping clear of rocks and the magic
item; every hit on another kind scores. With no paper left it rams rocks,
and the next scissor takes over. When the last scissor is gone the
game is over: the high scores show and a new game starts. It ends with q,
then n at the replay question."""
import math, random


from rec import Rec, UP, DOWN, LEFT, RIGHT

SECONDS = 45
r = Rec("scissor", "Scissor")
r.wait_for("CISSOR")
r.pump(1.0)

# key: (dy, dx); y u b n are the diagonals
MOVES = {UP: (-1, 0), DOWN: (1, 0), LEFT: (0, -1), RIGHT: (0, 1),
         "y": (-1, -1), "u": (-1, 1), "b": (1, -1), "n": (1, 1)}


def field():
    """Player position and the other items, outside the logo corner."""
    me, items = None, []
    buf = r.cells()
    for y in range(24):
        for x in range(80):
            if y < 8 and x < 14:
                continue
            c = buf[y][x]
            if c.data in "O#>?":
                if c.data == ">" and c.reverse:
                    me = (y, x)
                else:
                    items.append((c.data, y, x))
    return me, items


def dist(a, b):
    # rows are about twice as tall as columns are wide
    return math.hypot(2 * (a[0] - b[0]), a[1] - b[1])


def choose(me, items):
    papers = [(y, x) for t, y, x in items if t == "#"]
    danger = [(y, x) for t, y, x in items if t in "O?"]
    if not papers:
        # nothing left to cut: ram the nearest rock for the points, and the
        # next scissor takes over
        papers, danger = danger[:], []
    best, best_score = None, -1e9
    for key, (dy, dx) in MOVES.items():
        score = 0.0
        for step in (1, 2, 3):
            p = (me[0] + dy * step, me[1] + dx * step)
            if not (0 <= p[0] < 23 and 0 <= p[1] < 79):
                score -= 30
                break
            for d in danger:
                dd = dist(p, d)
                if dd < 5:
                    score -= (5 - dd) * 20 / step
        p = (me[0] + dy * 2, me[1] + dx * 2)
        if papers:
            score -= min(dist(p, q) for q in papers)
        score += random.uniform(0, 1.5)
        if score > best_score:
            best, best_score = key, score
    return best


def past_scores():
    t = r.text()
    if "lost The Game" in t:
        r.pump(2.0)
        r.key(" ", 0.8)
        t = r.text()
    if "Press a key to continue" in t:
        r.pump(1.5)
        r.key(" ", 0.8)


while r.elapsed() < SECONDS:
    past_scores()
    if "play again" in r.text():
        r.pump(2.0)
        r.key("y", 0.8)
        continue
    me, items = field()
    if not me:
        r.pump(0.1)
        continue
    r.key(choose(me, items), 0.12)
r.key("q", 1.0)
past_scores()
r.wait_for("play again", 3)
r.pump(1.5)
r.finish(b"n")
