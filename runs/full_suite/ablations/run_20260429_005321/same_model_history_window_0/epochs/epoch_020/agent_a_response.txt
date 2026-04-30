def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If no resources, drift away from opponent to reduce interference.
    if not resources:
        best = None
        best_d = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h:
                    continue
                if (nx, ny) in obs_set:
                    continue
                d = cheb(nx, ny, ox, oy)
                if d > best_d or (d == best_d and (nx, ny) < best):
                    best_d = d
                    best = (nx, ny)
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    # Target resource where we have the largest distance advantage over opponent.
    best_target = None
    best_adv = -10**9
    best_self_d = 10**9
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer
        if (adv > best_adv) or (adv == best_adv and (ds < best_self_d or (ds == best_self_d and (rx, ry) < best_target))):
            best_adv = adv
            best_self_d = ds
            best_target = (rx, ry)

    tx, ty = best_target
    cur_d = cheb(sx, sy, tx, ty)

    # Prefer move that reduces distance to target and maintains advantage.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            ds2 = cheb(nx, ny, tx, ty)
            do2 = cheb(ox, oy, tx, ty)
            adv2 = do2 - ds2
            # Sort key: prefer smaller ds2, then larger adv2, then deterministic position.
            moves.append((ds2, -adv2, nx, ny, dx, dy))
    moves.sort()

    for ds2, neg_adv2, nx, ny, dx, dy in moves:
        # If we can't improve, still take best candidate; staying is last.
        if dx == 0 and dy == 0 and ds2 < cur_d:
            continue
        return [dx, dy]

    return [0, 0]