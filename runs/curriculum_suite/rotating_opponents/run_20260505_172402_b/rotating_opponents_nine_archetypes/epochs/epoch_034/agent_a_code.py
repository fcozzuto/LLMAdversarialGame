def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 1))
    h = int(observation.get("grid_height", 1))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    opp_edge = (ox == 0 or ox == w - 1 or oy == 0 or oy == h - 1)
    best_dx, best_dy = 0, 0
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not free(nx, ny):
            continue
        d_opp = cheb(nx, ny, ox, oy)
        nearest = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < nearest:
                nearest = d
        score = 0
        if res:
            score += 1000000 - nearest * 1000
        score += d_opp * (2 if opp_edge else 1)
        if (nx, ny) == (ox, oy):
            score -= 10**9
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)):
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]