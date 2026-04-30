def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    res = {(p[0], p[1]) for p in resources}

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_mv = (0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if res:
            dist = min(cheb(nx, ny, rx, ry) for (rx, ry) in res)
        else:
            dist = cheb(nx, ny, ox, oy)
        collected = 1 if (nx, ny) in res else 0
        score = (collected, -dist, -cheb(nx, ny, ox, oy))
        if best is None or score > best:
            best = score
            best_mv = (dx, dy)
    return [best_mv[0], best_mv[1]]