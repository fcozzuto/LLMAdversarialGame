def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = w // 2, h // 2

    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        # prioritize resources where we are at least as close, and where we can race away from center
        center = cheb(rx, ry, cx, cy)
        key = (oppd - myd, -myd, center, -(rx * 8 + ry))
        if best is None or key > best:
            best = key
            tx, ty = rx, ry

    if best is None:
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        oppd2 = cheb(ox, oy, tx, ty)
        # race score: improve our relative position; tie-break by moving away from being "behind"
        val = (oppd2 - myd2, -myd2, -cheb(nx, ny, cx, cy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]