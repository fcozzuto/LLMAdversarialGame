def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    if not resources and observation.get("remaining_resource_count", 0) == 0:
        return [0, 0]

    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed:
        unclaimed = resources

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = (10**9, 10**9)
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        target_dist = 10**9
        if unclaimed:
            for tx, ty in unclaimed:
                d = abs(nx - tx) + abs(ny - ty)
                if d < target_dist:
                    target_dist = d
        opp_dist = abs(nx - ox) + abs(ny - oy)
        score = (target_dist, -opp_dist)
        if score < best:
            best = score
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]