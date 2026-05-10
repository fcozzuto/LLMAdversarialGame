def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("escape" in role) or ("runner" in role)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def adj_obs_pen(x, y):
        p = 0
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                p += 2
        return p

    def free_moves_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and (nx, ny) not in obs:
                c += 1
        return c

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy

        d = dist(nx, ny, ox, oy)
        pen = adj_obs_pen(nx, ny)
        fm = free_moves_count(nx, ny)
        edge = (nx in (0, w - 1)) + (ny in (0, h - 1))

        if is_evader:
            score = d + 0.3 * fm - 0.8 * pen + 0.05 * edge
            # prefer moving away from opponent deterministically
            score -= 0.02 * dist(nx, ny, 0, 0)
            score -= 0.02 * dist(nx, ny, w - 1, h - 1) * 0.2
        else:
            score = -d + 0.25 * fm - 0.9 * pen - 0.01 * edge
            # slight preference to reduce distance while not sticking to obstacles
            score -= 0.001 * dist(nx, ny, sx, sy)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]