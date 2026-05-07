def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (p[0], p[1])
            if r not in obs:
                res.append(r)
    if not res:
        return [0, 0]

    if (sx, sy) in res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_t = None
    best_key = None
    for rx, ry in res:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Prefer resources where we arrive earlier; otherwise, prefer ones still relatively close.
        key = (do - ds, ds, do, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd = md(nx, ny, tx, ty)
        o_after = md(ox, oy, tx, ty)
        # Safety: avoid stepping adjacent to obstacles (softly).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                x2, y2 = nx + ax, ny + ay
                if (x2, y2) in obs:
                    adj_obs += 1
        key = (-myd, o_after - (myd + 0.0001 * adj_obs), -adj_obs, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]