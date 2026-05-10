def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                unclaimed.append((x, y))

    if not unclaimed:
        targets = observation.get("opponent_territory") or []
        if targets:
            tx, ty = int(targets[0][0]), int(targets[0][1])
        else:
            return [0, 0]
    else:
        opp_bias = 2.0  # prefer cells far from opponent (center-claim opponent)
        best_val = 10**18
        tx, ty = sx, sy
        for x, y in unclaimed:
            d_us = abs(x - sx) + abs(y - sy)
            d_opp = abs(x - ox) + abs(y - oy)
            # Encourage quick expansion while resisting opponent proximity
            val = d_us - opp_bias * d_opp
            if val < best_val:
                best_val = val
                tx, ty = x, y

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the intended next cell is blocked, fall back to a safe directional alternative.
    nx, ny = sx + dx, sy + dy
    if ok(nx, ny):
        return [dx, dy]

    # Try axis moves first, then diagonals, then stay.
    candidates = [(dx, 0), (0, dy), (dx, dy), (0, 0)]
    for adx, ady in candidates:
        nx, ny = sx + adx, sy + ady
        if ok(nx, ny):
            return [adx, ady]

    return [0, 0]