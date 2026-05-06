def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = []
    resources = observation.get("resources") or []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in obstacles:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_target(tx, ty, x, y):
        return abs(x - tx) + abs(y - ty)

    best = (0, 0)
    best_val = None

    if res:
        tx, ty = min(res, key=lambda p: (score_target(p[0], p[1], sx, sy), p[0], p[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = score_target(tx, ty, nx, ny)
            if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)
    else:
        tx, ty = ox, oy
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = score_target(tx, ty, nx, ny)
            if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
                best_val = val
                best = (dx, dy)

    return [best[0], best[1]]