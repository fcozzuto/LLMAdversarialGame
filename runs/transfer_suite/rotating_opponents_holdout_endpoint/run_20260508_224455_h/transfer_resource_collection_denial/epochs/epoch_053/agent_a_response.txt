def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(x), int(y)) for x, y in obstacles_list)
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < int(observation["grid_width"]) and 0 <= y < int(observation["grid_height"])

    def risk_at(x, y):
        r = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    r += 1
        return r

    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        adv = do - ds
        val = 20 * adv - ds - 3 * risk_at(rx, ry)
        if val > best_val:
            best_val = val
            best = (int(rx), int(ry))

    tx, ty = best
    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Evaluate immediate move: prefer reaching target and denying opponent proximity.
    best_move = [0, 0]
    mv_best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ds2 = dist(nx, ny, tx, ty)
        do2 = dist(ox, oy, tx, ty)
        adv2 = do2 - ds2
        # slight bias to avoid moving into obstacle-nearby cells and to move onto resource
        on_res = 1 if (nx, ny) in set((int(x), int(y)) for x, y in resources) else 0
        val = 25 * adv2 - ds2 - 4 * risk_at(nx, ny) + 10 * on_res
        if val > mv_best:
            mv_best = val
            best_move = [dx, dy]

    return best_move