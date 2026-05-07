def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    best = None
    best_score = -10**18
    # Resource selection: maximize opponent delay + own advantage; if opponent is closer, prioritize intercept/deny targets.
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        adv = opd - myd  # positive means we are closer
        near = -myd
        # emphasize finishing race earlier; keep denominator small when near
        finish = (w + h) * 2 - myd
        # deny term: when we're behind, prefer targets that are also very close to opponent (so we can contest quickly)
        deny = 0
        if adv < 0:
            deny = 150 - myd  # higher when our move distance is small
        score = adv * 400 + near * 10 + finish * 2 + deny
        if score > best_score or (score == best_score and (best is None or (rx, ry) < best)):
            best_score = score
            best = (rx, ry)

    tx, ty = best
    best_move = [0, 0]
    best_move_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            myd = manh(nx, ny, tx, ty)
            # Local greedy: maximize progress toward chosen target; if equal, minimize risk by staying closer relative to opponent.
            opd = manh(ox, oy, tx, ty)
            score = (-myd) * 1000 + (opd - myd) * 5
            if score > best_move_score:
                best_move_score = score
                best_move = [dx, dy]

    return best_move