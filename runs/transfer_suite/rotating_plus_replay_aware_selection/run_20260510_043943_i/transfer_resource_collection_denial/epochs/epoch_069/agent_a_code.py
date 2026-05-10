def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = [0, 0]
    opp_has = (ox, oy)  # only used for deterministic tie-break

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # Evaluate best resource for this move by maximizing (opponent_arrival - self_arrival)
        best_r_key = None
        for rx, ry in resources:
            if not ok(rx, ry):
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Primary: time advantage (higher is better). Secondary: prefer earlier self, then farther opponent.
            # Final deterministic tie-break: resource coordinate sum, then opponent position.
            key = (od - sd, -sd, od, rx + ry, ox, oy)
            if best_r_key is None or key > best_r_key:
                best_r_key = key

        if best_r_key is None:
            continue

        # Prefer moves that lead to a stronger time advantage; tie-break deterministically.
        move_key = (best_r_key[0], best_r_key[1], best_r_key[2], best_r_key[3], best_r_key[4], best_r_key[5], dx, dy)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best_move = [dx, dy]

    return best_move