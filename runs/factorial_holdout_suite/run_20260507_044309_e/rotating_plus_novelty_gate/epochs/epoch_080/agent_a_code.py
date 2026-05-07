def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    # Immediate pickup preference (deterministic by move order)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2; a = -a if a < 0 else a
        b = y1 - y2; b = -b if b < 0 else b
        return a if a > b else b

    if resources:
        best_move = None
        best_score = -10**18
        for dx, dy, nx, ny in valid:
            my_best = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                advantage = opd - myd  # positive => we arrive no later than opponent
                # Slight preference for resources that are near my current "front" (towards opponent's y)
                front = -abs(ry - oy) * 0.1
                score = advantage * 10.0 - myd + front
                if score > my_best:
                    my_best = score
            # Small tie-break: prefer staying closer to current y to avoid oscillations
            tie = -abs(ny - sy) * 0.01 - abs(nx - sx) * 0.01
            total = my_best + tie
            if total > best_score:
                best_score = total
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: drift to reduce distance to opponent side (deterministic)
    target_x = 0 if sx > ox else w - 1
    target_y = oy
    best = (0, 0, cheb(sx, sy, target_x, target_y))
    for dx, dy, nx, ny in valid:
        d = cheb(nx, ny, target_x, target_y)
        if d < best[2]:
            best = (dx, dy, d)
    return [int(best[0]), int(best[1])]