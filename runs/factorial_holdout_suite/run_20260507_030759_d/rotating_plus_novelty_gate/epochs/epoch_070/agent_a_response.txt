def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    resset = set(res)

    if (sx, sy) in resset:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal or not res:
        return [0, 0]

    opp = (ox, oy)
    cur = (sx, sy)

    # One-step lookahead: choose move that makes us most advantaged toward a contested resource.
    best_move = None
    best_key = None
    for dx, dy in legal:
        nxt = (sx + dx, sy + dy)
        if nxt in resset:
            return [dx, dy]

        my_best = None
        # Prefer resources where (my_dist - opp_dist) is smallest; then smaller my_dist; then deterministic.
        for r in res:
            dm = manh(nxt, r)
            do = manh(opp, r)
            key = (dm - do, dm, r[0], r[1])
            if my_best is None or key < my_best:
                my_best = key

        # Slightly prefer moves that reduce our overall distance to the current best resource.
        # (But keep deterministic by using the same ordering tuple.)
        if best_key is None or my_best < best_key:
            best_key = my_best
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]