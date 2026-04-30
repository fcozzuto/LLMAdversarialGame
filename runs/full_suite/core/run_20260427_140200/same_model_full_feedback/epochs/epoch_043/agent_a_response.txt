def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        for rx, ry in resources:
            ds = manh(sx, sy, rx, ry)
            do = manh(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; penalize those opponent is closer to
            score = (ds - do, ds, rx, ry)
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
        opp_bias = (ox - sx, oy - sy)
    else:
        cx, cy = w // 2, h // 2
        # Drift toward center, but keep away from opponent
        tx, ty = cx - (1 if ox > cx else -1 if ox < cx else 0), cy - (1 if oy > cy else -1 if oy < cy else 0)
        opp_bias = (ox - sx, oy - sy)

    # Choose next move: minimize distance to target and maximize distance gap vs opponent.
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = manh(nx, ny, tx, ty)
        d_opp = manh(ox, oy, tx, ty)
        # If moving reduces self distance more than it reduces opponent distance (opponent stationary this turn).
        # Add small bias away from opponent to avoid easy contest.
        away = 0
        if resources:
            # bias away from opponent position slightly
            ax = nx - ox
            ay = ny - oy
            away = 0 if (ax == 0 and ay == 0) else (1 if (ax > 0 or (ax == 0 and ay > 0)) else 0)
        dist_gap = d_self - d_opp
        cand = (dist_gap, d_self, -((nx + ny) % 2), dx, dy)
        if cand[0] < best_move[0] or (cand[0] == best_move[0] and cand[1] < best_move[1]):
            best_move = (cand[0], cand[1], cand[3], cand[4])

    return [int(best_move[2]), int(best_move[3])]