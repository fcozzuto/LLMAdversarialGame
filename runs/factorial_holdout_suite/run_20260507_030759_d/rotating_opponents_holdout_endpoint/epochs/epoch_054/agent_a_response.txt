def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Move choice: maximize advantage in grabbing the same resource (race heuristic),
    # and secondarily prefer moves that reduce own distance.
    best = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        cur_best_adv = -10**9
        cur_best_own = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent (after move)
            if adv > cur_best_adv or (adv == cur_best_adv and ds < cur_best_own):
                cur_best_adv = adv
                cur_best_own = ds
        # Tie-break: prefer smaller opponent distance too, then deterministic ordering by move.
        opp_tie = min(man(ox, oy, r[0], r[1]) for r in resources if (man(nx, ny, r[0], r[1]) == cur_best_own)) \
            if resources else 0
        key = (cur_best_adv, -cur_best_own, -opp_tie, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]