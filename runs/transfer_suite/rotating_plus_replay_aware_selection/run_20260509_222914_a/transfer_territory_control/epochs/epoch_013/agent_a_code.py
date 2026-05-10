def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                obstacles.add((x, y))

    res = []
    r = observation.get("resources")
    if isinstance(r, (list, tuple)):
        for p in r:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                    res.append((x, y))
    if not res and isinstance(observation.get("remaining_resource_count"), int):
        pass

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        if res:
            d_res = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
        else:
            d_res = 10**9
        score = (d_res, d_opp)  # minimize distance to resource, then opponent
        if best_score is None or score < best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return best