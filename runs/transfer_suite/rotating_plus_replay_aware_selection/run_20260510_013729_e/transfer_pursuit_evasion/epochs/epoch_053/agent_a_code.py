def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    if not (0 <= sx < w and 0 <= sy < h):
        sx, sy = 0, 0

    deltas = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    def score_cell(x, y):
        if (x, y) in obs:
            return 10**9
        d = abs(x - ox) + abs(y - oy)
        adj = 0
        for tx, ty in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + tx, y + ty) in obs:
                adj += 1
        return d + adj * 0.25 + (abs(x - ox) == 1 and abs(y - oy) == 1) * 0.1

    best = None
    best_d = 10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            s = score_cell(nx, ny)
            if s < best_d:
                best_d = s
                best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]