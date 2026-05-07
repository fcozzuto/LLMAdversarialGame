def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

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

    best = None
    best_key = None
    for rx, ry in res:
        do = md(ox, oy, rx, ry)
        ds = md(sx, sy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise, still consider if it keeps us competitive.
        key = (ds - 0.6 * do, ds, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    opp_best = None
    opp_best_d = None
    for rx, ry in res:
        d = md(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d or (d == opp_best_d and (rx, ry) < opp_best):
            opp_best_d = d
            opp_best = (rx, ry)
    bx, by = opp_best

    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_t = md(nx, ny, tx, ty)
        d_o = md(nx, ny, bx, by)
        d_opp = md(nx, ny, ox, oy)
        # If we are in danger of being out-raced, prioritize creating distance from opponent.
        val = (-d_t) + 0.12 * d_opp + 0.03 * d_o
        # Deterministic tie-break: prefer diagonal, then right, then up, then stay.
        tie = (-(dx != 0 and dy != 0), -dx, -dy, 0 if (dx == 0 and dy == 0) else 1)
        key = (val, tie)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]