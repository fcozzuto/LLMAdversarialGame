def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]
    obstacle_set = set((x, y) for x, y in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target we can reach earlier (break ties by nearer and then position)
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we arrive earlier
        key = (margin, -ds, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue

        # Primary: improve arrival advantage to chosen target
        ds1 = cheb(nx, ny, tx, ty)
        do1 = cheb(ox, oy, tx, ty)
        lead = do1 - ds1

        # Secondary: if tie, move closer; also avoid stepping away from overall best lead
        dist_to_target = ds1
        self_to_best = -dist_to_target

        # Tertiary: prefer moves that don't "strand" us away from remaining resources
        # (cheap: only compare to best two margins)
        near_bonus = 0
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            o = cheb(ox, oy, rx, ry)
            near_bonus += 1 if (o - d) >= lead else 0
            if near_bonus >= 2:
                break

        val = (lead * 1000) + (self_to_best) + near_bonus
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move