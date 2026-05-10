def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Choose target resource where we are relatively closer than opponent.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer: maximize advantage (opd - myd), then smaller myd, then stable tie-break.
        key = (-(opd - myd), myd, (rx * 31 + ry) % 1000)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    res_set = set(tuple(p) for p in resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Encourage immediate collection.
        collect = 0
        if (nx, ny) in res_set:
            collect = 1

        # How competitive we remain for the chosen target.
        myd_next = cheb(nx, ny, tx, ty)
        opd_next = cheb(ox, oy, tx, ty)  # opponent hasn't moved yet this turn
        advantage_key = (myd_next - opd_next)

        # Small tie-break: move in direction of target, otherwise keep stability.
        dir_key = (0 if (tx - nx) == 0 else -1 if tx - nx < 0 else 1,
                    0 if (ty - ny) == 0 else -1 if ty - ny < 0 else 1)

        # Avoid stepping into a cell that would let opponent be closer to ANY resource.
        opp_pressure = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            if cheb(ox, oy, rx, ry) + 0 <= cheb(nx, ny, rx, ry):
                opp_pressure += 1

        key = (advantage_key, myd_next, -collect, opp_pressure, dir_key, (nx * 17 + ny) % 1000)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]