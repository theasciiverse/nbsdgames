"""Records asciiverse/casts/nbsd-sos.cast: the default setup, a human on
blue against the computer on yellow, answered at the two start-up
questions. The driver plays blue: it completes an S-O-S when it can,
otherwise writes a letter that leaves the computer no S-O-S to complete,
and only then anything else. Finished games are replayed with y."""
import random

from rec import Rec, UP, DOWN, LEFT, RIGHT

SECONDS = 45
H, W = 5, 6
r = Rec("nbsd-sos", "SOS")
r.wait_for("blue player", 5)
r.pump(0.8)
r.key("h", 0.8)              # blue: human
r.key("c", 0.8)              # yellow: computer
r.wait_for("(_'| |(_'")
r.pump(0.8)
cy = cx = 0


def board():
    rows = r.grid()
    return [[rows[4 + y][1 + 2 * x] for x in range(W)] for y in range(H)]


def at(b, y, x):
    return b[y][x] if 0 <= y < H and 0 <= x < W else None


def sos(b, y, x):
    """How many S-O-S lines the letter at (y, x) completes, as the game counts them."""
    n = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if not (dy or dx):
                continue
            if b[y][x] == "S" and at(b, y + dy, x + dx) == "O" and at(b, y + 2 * dy, x + 2 * dx) == "S":
                n += 2
            if b[y][x] == "O" and at(b, y + dy, x + dx) == "S" and at(b, y - dy, x - dx) == "S":
                n += 1
    return n // 2


def best_gain(b):
    g = 0
    for y in range(H):
        for x in range(W):
            if b[y][x] == ".":
                for c in "SO":
                    b[y][x] = c
                    g = max(g, sos(b, y, x))
                    b[y][x] = "."
    return g


def choose(b):
    moves = []
    for y in range(H):
        for x in range(W):
            if b[y][x] == ".":
                for c in "SO":
                    b[y][x] = c
                    moves.append((sos(b, y, x), -best_gain(b), random.random(), y, x, c))
                    b[y][x] = "."
    return max(moves)[3:] if moves else None


def go(y, x):
    global cy, cx
    while cy < y: r.key(DOWN, 0.06); cy += 1
    while cy > y: r.key(UP, 0.06); cy -= 1
    while cx < x: r.key(RIGHT, 0.06); cx += 1
    while cx > x: r.key(LEFT, 0.06); cx -= 1


while r.elapsed() < SECONDS:
    t = r.text()
    if "again" in t:
        if r.elapsed() > SECONDS - 10:
            break
        r.pump(2.5)
        r.key("y", 0.8)
        cy = cx = 0
        continue
    if "Thinking" in t:
        r.pump(0.2)
        continue
    move = choose(board())
    if not move:
        r.pump(0.3)
        continue
    y, x, c = move
    go(y, x)
    r.pump(0.25)
    r.key(c, 0.8)
r.pump(1.5)
r.finish(b"n" if "again" in r.text() else b"q")
