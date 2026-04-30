def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    safe = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            safe.append((dx, dy, nx, ny))
    if not safe:
        return [0, 0]

    opp_step = max(abs(sx - ox), abs(sy - oy))
    best_move = None

    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            if best is None or (opd - myd, -myd, rx, ry) > best[0]:
                best = ((opd - myd, -myd, rx, ry), (rx, ry))
        tx, ty = best[1]
        target = None
        for dx, dy, nx, ny in safe:
            myd2 = dist((nx, ny), (tx, ty))
            score = (-(myd2), -(dist((nx, ny), (ox, oy))), nx, ny)
            if target is None or score > target[0]:
                target = (score, dx, dy)
        best_move = (target[1], target[2])
    else:
        best = None
        for dx, dy, nx, ny in safe:
            score = (dist((nx, ny), (ox, oy)), -abs(nx - (w - 1)) - abs(ny - (h - 1)))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        best_move = (best[1], best[2])

    if opp_step <= 1 and resources:
        # If we're adjacent to opponent, prefer moves that increase distance from them.
        best = None
        for dx, dy, nx, ny in safe:
            score = (max(abs(nx - ox), abs(ny - oy)), -dist((nx, ny), best[1]) if best else 0)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        best_move = (best[1], best[2])

    return [int(best_move[0]), int(best_move[1])]