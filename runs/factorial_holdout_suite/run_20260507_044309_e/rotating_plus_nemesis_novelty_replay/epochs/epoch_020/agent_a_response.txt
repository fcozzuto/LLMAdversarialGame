def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = None

    # Pre-filter feasible resources
    feas = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        feas.append((rx, ry))
    if not feas:
        return [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = 0
        if ny < 0: ny = 0
        if nx >= w: nx = w - 1
        if ny >= h: ny = h - 1
        if (nx, ny) in obstacles:
            continue

        # Choose best target under our hypothetical move
        # Value: how much closer we are than opponent, plus preference for near-term capture,
        # plus a small deny term if target is on opponent's current row.
        local_best = None
        for rx, ry in feas:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            deny = 2.5 if ry == oy else 0.0
            urgency = -0.25 * sd
            near = -0.05 * abs(rx - nx) - 0.05 * abs(ry - ny)
            val = adv + deny + urgency + near
            if local_best is None or val > local_best:
                local_best = val

        if local_best is None:
            continue

        # Break ties: avoid moves that increase our distance to the currently best target region
        tie = -cheb(nx, ny, nx, ny)
        move_val = local_best + 0.0 * tie

        if best_val is None or move_val > best_val:
            best_val = move_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]