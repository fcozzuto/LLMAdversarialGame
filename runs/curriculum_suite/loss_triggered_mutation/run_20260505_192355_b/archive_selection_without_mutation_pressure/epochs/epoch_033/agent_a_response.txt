def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Sweep_rows opponent: strongly align with opponent's row to contest their path
    preferred_resources = [r for r in resources if abs(r[1] - oy) <= 1]
    target_pool = preferred_resources if preferred_resources else resources

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by the best single resource in the pool, but reward row alignment
        local_best = None
        for rx, ry in target_pool:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            adv = opd - myd  # >=0 => we arrive no later
            winflag = 1 if adv >= 0 else 0

            # Break ties by: (1) competitive advantage, (2) resource proximity, (3) row alignment
            align = -abs(ny - oy)  # higher is better (closer to opponent row)
            progress = -myd
            # mild diversification: prefer resources that are not exactly behind the opponent row
            row_pen = -abs(ry - oy)
            key = (winflag, adv, align, progress, row_pen)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # Global tie-break: also keep our next step not too far from opponent (helps row contesting)
        global_key = (local_best[0], local_best[1], local_best[2], local_best[3], -manh(nx, ny, ox, oy), dx, dy)
        if best is None or global_key > best[0]:
            best = (global_key, [dx, dy])

    return best[1] if best else [0, 0]