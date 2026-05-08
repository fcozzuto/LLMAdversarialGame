def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    mx, my = (sx + ox) // 2, (sy + oy) // 2

    def prox(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    c += 1
        return c

    def align_score(x, y):
        dx1, dy1 = ox - x, oy - y
        step_dx = 0 if dx1 == 0 else (1 if dx1 > 0 else -1)
        step_dy = 0 if dy1 == 0 else (1 if dy1 > 0 else -1)
        adx = step_dx * (1 if x > sx else (-1 if x < sx else 0))
        ady = step_dy * (1 if y > sy else (-1 if y < sy else 0))
        return adx + ady

    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = cheb(nx, ny, ox, oy)
        d_mid = cheb(nx, ny, mx, my)
        p = prox(nx, ny)
        # Prefer smaller distance to opponent, then smaller to mid intercept line, then safer from obstacles.
        score = (-10.0 * d_opp) + (-1.2 * d_mid) + (-0.7 * p) + (0.05 * align_score(nx, ny))

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]