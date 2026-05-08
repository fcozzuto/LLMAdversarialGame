def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles) if obstacles else set()
    resources = observation.get("resources", [])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    targets = [tuple(r) for r in resources] if resources else []
    if targets:
        tx, ty = min(targets, key=lambda p: md(sx, sy, p[0], p[1]))
        target = (tx, ty)
    else:
        target = (ox, oy)

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dcur = md(sx, sy, target[0], target[1])
        dnew = md(nx, ny, target[0], target[1])
        v = (dcur - dnew) * 10 - (1 if (nx, ny) == (ox, oy) else 0)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
        elif v == bestv and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]