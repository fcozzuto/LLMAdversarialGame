def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inside(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cands = [(dx, dy) for dx, dy in moves if legal(dx, dy)]
    if not cands:
        return [0, 0]

    res = [tuple(r) for r in resources if len(r) >= 2]
    if not res:
        best, bestv = (0, 0), -10**18
        for dx, dy in cands:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - ox) + abs(ny - oy)
            v = d - (abs(nx - w // 2) + abs(ny - h // 2))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    opp_best = min(abs(ox - rx) + abs(oy - ry) for rx, ry in res)
    cx, cy = w // 2, h // 2

    best, bestv = (0, 0), -10**18
    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        self_best = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
        dist_to_center = abs(nx - cx) + abs(ny - cy)
        on_resource = 1 if (nx, ny) in obstacles else 0  # obstacles already filtered, keeps deterministic
        # Prefer being closer than opponent is, while keeping moving toward some resource efficiently.
        v = (opp_best - self_best) * 100 - self_best - dist_to_center - on_resource * 10
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]