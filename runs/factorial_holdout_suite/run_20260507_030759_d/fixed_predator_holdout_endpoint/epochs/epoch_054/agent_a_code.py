def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((x, y) for x, y in obstacles)

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue

        # Look for the best resource we could contest after this move.
        local_best_adv = None
        local_best_md = None
        local_best_od = None
        for rx, ry in resources:
            myd = cheb((nx, ny), (rx, ry))
            opd = cheb((ox, oy), (rx, ry))
            adv = opd - myd  # positive means we're closer
            if local_best_adv is None or adv > local_best_adv or (adv == local_best_adv and myd < local_best_md):
                local_best_adv = adv
                local_best_md = myd
                local_best_od = opd

        # Tie-break: prefer moves that keep distance from opponent a bit and approach target closely.
        key = (local_best_adv, -local_best_od, -local_best_md, -nx, -ny, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        # If all legal moves are blocked (rare), stay.
        return [0, 0]
    return [best[0], best[1]]