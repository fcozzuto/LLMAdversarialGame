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
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in set(res):
        return [0, 0]

    # Pick best target resource by who can reach first (favor positive gap: I'm closer)
    best_r = None
    best_key = None
    for r in res:
        myd = md((sx, sy), r)
        oppd = md((ox, oy), r)
        # primary: oppd - myd, secondary: smaller myd, tertiary: smaller oppd, final: lex
        key = (oppd - myd, -myd, -oppd, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Choose move that improves my gap to target, tie-break by decreasing distance to target
    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = md((nx, ny), (tx, ty))
        oppd = md((ox, oy), (tx, ty))
        val = (oppd - myd, -myd, -(abs(nx - ox) + abs(ny - oy)), -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]