"""Records asciiverse/casts/darrt.cast: two rounds of ten shots, played by a
driver that reads the letters off the screen frame by frame, works out
where each one is heading, and stops the letter that will come to rest
nearest the centre of the target (a stopped letter travels 14 more frames).
The second round's play-again question is answered with n."""
import math


from rec import Rec, ENTER


SECONDS = 30          # no new round starts after this
LEN, WID = 24, 80
CY, CX = LEN // 2, WID // 2
TRAVEL = 14
r = Rec("darrt", "Darrt")
r.wait_for("ARRT")
r.pump(0.5)


def letters():
    """The moving letters: {letter: (y, x)}; stopping and landed ones are bold."""
    buf = r.cells()
    found = {}
    for y in range(LEN):
        line = buf[y]
        for x in range(WID):
            c = line[x]
            if "A" <= c.data <= "Z" and c.fg == "green" and not c.bold:
                found[c.data] = (y, x)
    return found


def miss(y, x):
    """The game's own distance from the centre (rows count double)."""
    return math.sqrt((y - CY) ** 2 + 0.25 * (x - CX) ** 2)


def fit(track):
    """Velocity (vy, vx) and current position from a straight run of frames."""
    n = len(track)
    ts = [t for t, _, _ in track]
    mt = sum(ts) / n
    var = sum((t - mt) ** 2 for t in ts)
    my = sum(y for _, y, _ in track) / n
    mx = sum(x for _, _, x in track) / n
    vy = sum((t - mt) * (y - my) for t, y, _ in track) / var
    vx = sum((t - mt) * (x - mx) for t, _, x in track) / var
    norm = math.hypot(vy, vx)
    if norm > 0.3:
        vy, vx = vy / norm, vx / norm
    t = ts[-1]
    return vy, vx, my + vy * (t - mt) + 0.5, mx + vx * (t - mt) + 0.5


def predict(y, x, vy, vx, steps):
    """Follows the game's bounces off the screen edges and the logo corner."""
    bounces = 0
    for _ in range(steps):
        if x < 0 or int(x) >= WID - 1 or (int(x) == 13 and y <= 7):
            vx, bounces = -vx, bounces + 1
        if y < 0 or int(y) >= LEN - 1 or (x <= 13 and int(y) == 7):
            vy, bounces = -vy, bounces + 1
        y, x = y + vy, x + vx
    return y, x, bounces


tracks, frame, last_seen, last_shot = {}, 0, None, 0.0
while True:
    text = r.text()
    if "Press any key to continue" in text or "Press a key to continue" in text:
        r.pump(1.5)          # let the landed letters be seen
        r.key(ENTER, 1.0)
        continue
    if "Wanna play again" in text:
        r.pump(1.5)
        if r.elapsed() > SECONDS:
            break
        r.key("y", 0.5)
        tracks, last_seen, last_shot = {}, None, r.elapsed()
        continue
    now = letters()
    if now == last_seen:
        r.pump(0.02)
        continue
    last_seen = now
    frame += 1
    for c, (y, x) in now.items():
        t = tracks.setdefault(c, [])
        if t and frame - t[-1][0] > 3:
            t.clear()
        if len(t) >= 2:
            dy0, dx0 = t[-1][1] - t[-2][1], t[-1][2] - t[-2][2]
            dy1, dx1 = y - t[-1][1], x - t[-1][2]
            if dy0 * dy1 < 0 or dx0 * dx1 < 0:      # it bounced: start over
                del t[:-1]
        t.append((frame, y, x))
        del t[:-12]
    for c in list(tracks):
        if c not in now:
            del tracks[c]
    # the longer since the last shot, the less exact a shot has to be
    wait = r.elapsed() - last_shot
    best, best_miss = None, 1.5 + max(0.0, wait - 1.2) * 3
    for c, t in tracks.items():
        if len(t) < 5 or c == "Q":      # q also asks to quit the round
            continue
        vy, vx, y, x = fit(t)
        py, px, bounces = predict(y, x, vy, vx, TRAVEL)
        m = miss(py, px) + bounces * 1.5
        if m < best_miss:
            best, best_miss = c, m
    if best and wait > 0.8:
        r.key(best.lower(), 0.02)
        last_shot = r.elapsed()
        del tracks[best]
    else:
        r.pump(0.02)
r.finish(b"n")
