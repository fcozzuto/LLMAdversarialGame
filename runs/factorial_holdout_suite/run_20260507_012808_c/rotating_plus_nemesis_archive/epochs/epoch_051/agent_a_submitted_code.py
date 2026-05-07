def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res.append((x, y))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = [m for m in moves if ok(sx + m[0], sy + m[1])]
    if not moves:
        return [0, 0]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if res:
            target = min(res, key=lambda t: dist(ox, oy, t[0], t[1]))
            myd = dist(nx, ny, target[0], target[1])
            oppd = dist(ox, oy, target[0], target[1])
            val = (myd, -oppd, dx == 0 and dy == 0)
        else:
            val = (dist(nx, ny, ox, oy), dx == 0 and dy == 0)
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1]]]