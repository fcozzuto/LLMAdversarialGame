def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        if unclaimed:
            best_duel = 10**9
            best_d = 10**9
            for x, y in unclaimed[:50]:
                dS = dist(nx, ny, x, y)
                dO = dist(ox, oy, x, y)
                duel = dS - dO
                if duel < best_duel:
                    best_duel, best_d = duel, dS
                elif duel == best_duel and dS < best_d:
                    best_d = dS
            center = abs(nx - cx) + abs(ny - cy)
            val = -best_duel * 10 - best_d - center * 0.01 - (nx + ny) * 1e-6
        else:
            val = -dist(nx, ny, cx, cy) - 0.3 * dist(nx, ny, ox, oy)
        if best is None or val > best[0]:
            best = (val, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2]]]