def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]
    cx = max(0, min(w - 1, sx))
    cy = max(0, min(h - 1, sy))
    best = None
    bestv = None
    for rx, ry in resources:
        ds = abs(rx - cx) + abs(ry - cy)
        do = abs(rx - ox) + abs(ry - oy)
        v = (do - ds) - 0.01 * ds
        key = (v, -do, -ds, rx, ry)
        if best is None or key > bestv:
            bestv = key
            best = (rx, ry)
    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    bestmv = None
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        ds1 = abs(tx - nx) + abs(ty - ny)
        hit = 1.0 if (nx, ny) == (tx, ty) else 0.0
        # If we move closer, slightly encourage also increasing opponent distance.
        do1 = abs(ox - nx) + abs(oy - ny)
        score = -ds1 + 2.5 * hit + 0.02 * do1
        # Small deterministic tie-breaker.
        score2 = score - 0.0001 * (nx * 8 + ny)
        if bestmv is None or score2 > bestmv:
            bestmv = score2
            bestm = (dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]