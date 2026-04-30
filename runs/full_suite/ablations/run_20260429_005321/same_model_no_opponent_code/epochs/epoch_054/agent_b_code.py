def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate moves (deterministic order)
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            cands.append((dx, dy))

    if not cands:
        return [0, 0]
    if not resources:
        # Head to opponent's corner to reduce their options
        target_x = w - 1 if sx < w - 1 else 0
        target_y = h - 1 if sy < h - 1 else 0
        best = None
        best_val = -10**18
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - target_x) + abs(ny - target_y)
            val = -d
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    # Heuristic:
    # Prefer moves that reduce distance to the closest resource,
    # while also increasing the distance advantage over the opponent for that resource.
    best = None
    best_val = -10**18
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        # Obstacle proximity penalty (avoid "sticking" at obstacle walls)
        near_obs = 0
        for ex, ey in obstacles_list:
            if abs(nx - ex) <= 1 and abs(ny - ey) <= 1:
                near_obs += 1

        min_ds = 10**9
        best_adv = -10**9
        best_block = -10**9
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            adv = do - ds  # positive means we are closer to this resource than opponent
            if ds < min_ds:
                min_ds = ds
            if adv > best_adv:
                best_adv = adv
            # Blocking: if we could reach before/at the opponent for some resource, reward it
            # (simple timing proxy)
            if adv >= 0:
                block = 2 - ds
                if block > best_block:
                    best_block = block

        # Tie-breakers: closeness, then maximize advantage, then minimize enemy distance after move.
        dist_score = -min_ds
        adv_score = best_adv
        enemy_after = abs(nx - ox) + abs(ny - oy)
        enemy_score = -enemy_after
        # Weighting tuned to be stable and decisive
        val = 3.0 * dist_score + 4.0 * adv_score + 1.2 * enemy_score + 1.5 * best_block - 0.8 * near_obs
        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]