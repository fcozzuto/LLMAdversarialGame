def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_move_for_target(tx, ty):
        best = None
        bestd = 10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    if resources:
        adj = [(rx, ry) for rx, ry in resources if md(ox, oy, rx, ry) == 1]
        if adj:
            tx, ty = min(adj, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
            return best_move_for_target(tx, ty)

        tx, ty = min(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))
        return best_move_for_target(tx, ty)

    best = None
    bestv = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = md(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return list(best) if best is not None else [0, 0]