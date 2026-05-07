def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (0, h - 1) if (sx + sy) <= (ox + oy) else (w - 1, 0)
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            # Prefer not to step closer to opponent if we can't collect.
            oppd = man(nx, ny, ox, oy)
            key = (oppd, -d, -nx, -ny)
            if key > best:
                best = key
                bx, by = dx, dy
        return [bx, by]

    # Prefer resources where we can arrive earlier; if forced, prioritize closest while reducing opponent pressure.
    opp_adj_risk = set()
    for rx, ry in resources:
        if man(ox, oy, rx, ry) <= 1:
            opp_adj_risk.add((rx, ry))

    best_key = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Evaluate best target from this move.
        local_best = (-10**9, 0, 0)
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            margin = od - sd  # positive if we are earlier
            risk = 0
            if (rx, ry) in opp_adj_risk and sd > od:
                risk = 2000  # avoid giving away next-step denials
            # Additional preference: reduce distance to target and keep away from opponent.
            opp_after = man(nx, ny, ox, oy)
            key = (margin * 10 - sd - risk, opp_after, -rx, -ry)
            if key > local_best:
                local_best = key
        if best_key is None or local_best > best_key:
            best_key = local_best
            best_move = [dx, dy]

    return best_move