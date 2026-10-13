"""Records asciiverse/casts/tugow.cast: the player reads the next digit off
the "Type!" line and types it, quickly at first so the rope is pulled over
and the levels go up, then too slowly for the faster pull at level 4,
until the rope is lost; the high scores show and a second game starts,
which is ended with q (past the trophy for a new best score, if
it shows), then n at the replay question."""
import random

from rec import Rec

SECONDS = 42
r = Rec("tugow", "Tug of War")
r.wait_for("Type!")
r.pump(1.0)


def next_char():
    rows = r.grid()
    for i, line in enumerate(rows[:-1]):
        c = line.find("Type!")
        if c >= 0:
            s = rows[i + 1][c:].strip()
            return s[0] if s else None
    return None


def level():
    for line in r.grid():
        if "Level:" in line:
            return int(line.split("Level:")[1].split()[0])
    return 0


games = 0
def past_record():
    """A new best score shows a trophy first, until a key is pressed."""
    if "Press a key to continue" in r.text():
        r.pump(2.0)
        r.key(" ", 0.8)


while r.elapsed() < SECONDS:
    past_record()
    if "play again" in r.text():
        r.pump(2.5)          # let the high scores be seen
        games += 1
        r.key("y", 0.8)
        continue
    ch = next_char()
    if ch is None:
        r.pump(0.1)
        continue
    lv = level()
    # a quick typist up to level 4, then too slow for the faster pull, so the
    # first game is lost and the score table shows; the second game is quick
    gap = 0.12 if lv < 4 or games else random.uniform(0.5, 0.8)
    if games and r.elapsed() > SECONDS - 6:
        break
    if random.random() < 0.05:
        r.key(random.choice("0123456789"), gap)   # a slip of the finger
    else:
        r.key(ch, gap)
r.key("q", 1.5)
past_record()
r.wait_for("play again", 3)
r.pump(1.5)
r.finish(b"n")
