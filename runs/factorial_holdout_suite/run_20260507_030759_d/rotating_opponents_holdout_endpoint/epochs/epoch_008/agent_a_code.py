def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if not w or not h:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)
    resources = observation.get("resources", []) or []
    if not resources:
        resources = [(ox, oy)]
    targets = []
    for r in resources:
        rx, ry = r[0], r[1]
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
            targets.append((rx, ry))
    if not targets:
        targets = [(ox, oy)]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in targets:
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            if d1 < my_best:
                my_best = d1
            if d2 < opp_best:
                opp_best = d2
        # Prefer moves that get us closer to the closest resource relative to opponent.
        key = (my_best - opp_best, my_best, man(nx, ny, ox, oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move