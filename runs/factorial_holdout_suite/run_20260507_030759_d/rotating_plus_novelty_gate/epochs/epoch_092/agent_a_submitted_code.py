def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                res.append((x, y))

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if (sx, sy) in res:
        return [0, 0]

    best = None
    best_self = 10**18
    best_opp = 10**18
    for rx, ry in res:
        d_self = md(sx, sy, rx, ry)
        d_opp = md(ox, oy, rx, ry)
        if d_self <= d_opp:
            if d_self < best_self or (d_self == best_self and d_opp < best_opp):
                best = (rx, ry)
                best_self, best_opp = d_self, d_opp
    if best is None:
        for rx, ry in res:
            d_self = md(sx, sy, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            if best is None or d_self < best_self or (d_self == best_self and d_opp < best_opp):
                best = (rx, ry)
                best_self, best_opp = d_self, d_opp

    tx, ty = best
    best_move = None
    best_dist = 10**18
    for dx, dy in dirs:
        if (dx, dy) not in legal:
            continue
        nx, ny = sx + dx, sy + dy
        d = md(nx, ny, tx, ty)
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]