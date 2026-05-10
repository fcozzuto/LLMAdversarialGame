def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    tx, ty = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = [tuple(p) for p in (observation.get("unclaimed_cells") or [])]
    resources = [tuple(p) for p in (observation.get("resources") or [])]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        best = None
        bd = 10**9
        for x, y in unclaimed:
            d = abs(x - sx) + abs(y - sy)
            if d < bd:
                bd = d
                best = (x, y)
        gx, gy = best
    elif resources:
        best = None
        bd = 10**9
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bd:
                bd = d
                best = (x, y)
        gx, gy = best
    else:
        gx, gy = tx, ty

    best_move = (0, 0)
    best_dist = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(gx - nx) + abs(gy - ny)
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]