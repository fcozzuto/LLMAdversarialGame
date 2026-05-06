def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Choose target resource where we can deny best (have reach advantage now).
    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = manh(sx, sy, rx, ry)
        oppd = manh(ox, oy, rx, ry)
        key = (-(oppd - myd), myd, -oppd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)
    tx, ty = best_res

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        if v < lo: return lo
        if v > hi: return hi
        return v

    # Score candidate next cells: maximize denial over all resources, with obstacle/boundary avoidance.
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        nx = clamp(nx, 0, w - 1)
        ny = clamp(ny, 0, h - 1)

        if (nx, ny) in obstacles:
            s = -10**9
        else:
            myd_t = manh(nx, ny, tx, ty)
            oppd_t = manh(ox, oy, tx, ty)
            # Deny term: bigger means we're getting closer than opponent.
            deny = oppd_t - myd_t

            # Secondary: evaluate over all resources for more robust greedy switching.
            best_deny_all = None
            best_my_all = None
            for rx, ry in resources:
                myd = manh(nx, ny, rx, ry)
                oppd = manh(ox, oy, rx, ry)
                d = oppd - myd
                if best_deny_all is None or (d, -myd, rx, ry) > (best_deny_all, -best_my_all, -10**9, -10**9):
                    best_deny_all = d
                    best_my_all = myd

            # Favor lower own distance to target when denial is similar.
            s = (best_deny_all * 5.0) + (deny * 1.5) - (myd_t * 0.08) - (abs(nx - sx) + abs(ny - sy)) * 0.01

        if best_score is None or s > best_score:
            best_score = s
            best_move = [dx, dy]

    return best_move