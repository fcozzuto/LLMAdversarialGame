def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    occ = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Prefer moves that let us arrive earlier to a contested resource (or minimize being behind),
    # using Manhattan distance rather than Chebyshev to adjust to diagonal-denial behavior.
    best_move = (0, 0)
    best_key = (-10**18, 10**18, -10**18)  # (adv, -myd, corner_bias)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        local_best = (-10**18, -10**18, -10**18)
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd
            corner_bias = -((rx + ry) % 2)  # deterministic mild tie-break
            key = (adv, -myd, corner_bias)
            if key > local_best:
                local_best = key
        # Then rank moves by their best achievable key
        if local_best > best_key:
            best_key = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]