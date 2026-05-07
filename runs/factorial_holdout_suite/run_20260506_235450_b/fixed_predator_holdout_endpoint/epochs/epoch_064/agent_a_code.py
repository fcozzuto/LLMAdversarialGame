def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (-(od - sd), sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    best_move = [0, 0]
    best_key = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            # Prefer moving closer to target while keeping opponent not closer.
            sd2 = cheb(nx, ny, tx, ty)
            od2 = cheb(ox, oy, tx, ty)
            # Also lightly avoid stepping away from current best overall.
            key = (-(od2 - sd2), sd2, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return best_move