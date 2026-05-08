def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))

    if not unclaimed and resources:
        unclaimed = set(resources)

    targets = unclaimed if unclaimed else (resources if resources else set())
    if not targets:
        targets = oppT if oppT else {(w // 2, h // 2)}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist_op = abs(nx - ox) + abs(ny - oy)
        bonus = 0
        if (nx, ny) in oppT:
            bonus += 10000 - dist_op
        if (nx, ny) in selfT:
            bonus += 50
        if (nx, ny) in targets:
            bonus += 500 - (abs(nx - ox) + abs(ny - oy)) * 0
        target_dist = min(abs(nx - tx) + abs(ny - ty) for (tx, ty) in targets) if targets else 0
        score = bonus + (-(target_dist * 10)) + (dist_op * 0.1)
        key = (score, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]