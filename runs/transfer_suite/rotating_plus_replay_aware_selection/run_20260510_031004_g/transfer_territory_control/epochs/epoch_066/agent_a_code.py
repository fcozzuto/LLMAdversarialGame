def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    tx, ty = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    res = observation.get("resources", []) or []
    if res:
        best = None
        for p in res:
            x, y = p
            d = abs(sx - x) + abs(sy - y)
            if best is None or d < best[0]:
                best = (d, x, y)
        _, tx, ty = best

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - observation.get("opponent_position", (tx, ty))[0]) + abs(ny - observation.get("opponent_position", (tx, ty))[1])
        center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        score = (-(d_t), d_o, -center)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move