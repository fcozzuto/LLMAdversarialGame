def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    res_set = set(tuple(p) for p in resources)

    # Pick a target resource: balance closeness for self vs opponent
    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        do = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        if ds == 0:
            val = 10**12
        else:
            val = 1000000 // (ds + 1) - 1200000 // (do + 1)
        # slight bias to nearer-to-center to reduce dithering
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dc = (rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)
        val -= int(dc)
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best if best is not None else (ox, oy)

    def move_score(nx, ny):
        if (nx, ny) in obstacles:
            return -10**18
        if not inb(nx, ny):
            return -10**18
        dtarget = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        dop = (ox - nx) * (ox - nx) + (oy - ny) * (oy - ny)
        bonus = 0
        if (nx, ny) in res_set:
            bonus += 10**9
        # If we are adjacent to opponent, prefer moves that keep distance
        adj = max(abs(ox - nx), abs(oy - ny)) <= 1
        if adj:
            bonus += 20000 if dop >= (ox - sx) * (ox - sx) + (oy - sy) * (oy - sy) else -5000
        # Encourage progress while discouraging collapsing onto opponent
        return bonus + (2000000 // (dtarget + 1)) + (2000 * dop)

    best_move = (0, 0)
    best_ms = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ms = move_score(nx, ny)
        if ms > best_ms:
            best_ms = ms
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]