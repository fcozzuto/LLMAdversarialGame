def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not deltas:
        return [0, 0]

    def clamp(px, py):
        if px < 0: px = 0
        if py < 0: py = 0
        if px >= w: px = w - 1
        if py >= h: py = h - 1
        return px, py

    # Pick a target that we are likely to reach earlier than opponent.
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        ds = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        do = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        if ds == 0:
            return [0, 0]
        # Advantage: positive when we are closer.
        adv = do - ds
        # Slight bias away from obstacles (prefer resources with more free vicinity).
        near_obs = 0
        for ex, ey in ((rx - 1, ry), (rx + 1, ry), (rx, ry - 1), (rx, ry + 1), (rx - 1, ry - 1), (rx + 1, ry + 1), (rx - 1, ry + 1), (rx + 1, ry - 1)):
            if (ex, ey) in obs_set:
                near_obs += 1
        s = adv - 0.8 * near_obs + (10**-6) * (rx + 3 * ry)
        if s > best_score:
            best_score = s
            best_t = (rx, ry)

    if best_t is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    # Evaluate next moves.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obs_set:
            continue
        # Lower distance to target; higher relative advantage to opponent.
        dn = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        dp = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        # Relative change if we move there.
        rel = dp - dn
        # Prefer staying out of immediate obstacle pressure.
        press = 0
        for ex, ey in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)):
            if (ex, ey) in obs_set:
                press += 1
        # Encourage approach when opponent is also near target: a bit more contest pressure.
        opp_dist_to_next = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        val = rel - 0.03 * dn - 1.2 * press - 0.001 * (abs(nx - ox) + abs(ny - oy)) - 0.0001 * opp_dist_to_next + (0.000001) * (dx * 7 + dy * 11)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]