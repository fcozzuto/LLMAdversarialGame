def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs and 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dsq(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def best_target():
        if not res:
            return ((w - 1) / 2.0, (h - 1) / 2.0)
        best = res[0]
        bestv = None
        for (rx, ry) in res:
            dse = dsq(sx, sy, rx, ry)
            doe = dsq(ox, oy, rx, ry)
            v = (doe - dse) * 10 + (-dse)
            if bestv is None or v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    tx, ty = best_target()

    def min_res_dist(nx, ny):
        if not res:
            return 0
        m = None
        for (rx, ry) in res:
            d = dsq(nx, ny, rx, ry)
            if m is None or d < m:
                m = d
        return m if m is not None else 0

    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            s = -10**9  # strongly avoid invalid/blocked
        else:
            d_to_target = dsq(nx, ny, int(tx), int(ty))
            d_opp_to_target = dsq(ox, oy, int(tx), int(ty))
            # maximize our advantage on the chosen target, while getting close to any resource
            s = 0
            s += (d_opp_to_target - d_to_target) * 2
            s += -min_res_dist(nx, ny)
            # bias toward central progress to reduce path traps
            cx = (w - 1) / 2.0
            cy = (h - 1) / 2.0
            s += -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.02
            # slight determinism in tie-breaking toward lower dx then lower dy
        if best_score is None or s > best_score or (s == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = s
            best_move = [dx, dy]
    return best_move