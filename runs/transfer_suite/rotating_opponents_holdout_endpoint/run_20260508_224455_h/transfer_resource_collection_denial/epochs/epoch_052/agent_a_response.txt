def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)

    def dist(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir

    def risk(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    if not resources:
        return [0, 0]

    # Pick target with maximal advantage (being closer than opponent), tie-break by closeness and safety.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer
        val = 12 * adv - ds - 2 * risk(rx, ry)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_m = (0, 0)
    best_mv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist(nx, ny, tx, ty)
        # Slightly prefer moves that keep we still closer than opponent to same target.
        nod = dist(ox, oy, tx, ty)
        val = -5 * nd - 3 * risk(nx, ny) + 2 * (nod - nd)
        if val > best_mv:
            best_mv = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]