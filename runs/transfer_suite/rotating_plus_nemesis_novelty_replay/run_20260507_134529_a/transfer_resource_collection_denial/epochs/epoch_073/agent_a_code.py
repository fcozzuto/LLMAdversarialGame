def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if resources:
        target = resources[0]
        bd = cheb(sx, sy, target[0], target[1])
        for rx, ry in resources[1:]:
            d = cheb(sx, sy, rx, ry)
            if d < bd:
                bd = d
                target = (rx, ry)
    else:
        target = (w // 2, h // 2)

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        dres = cheb(nx, ny, target[0], target[1])
        dop = cheb(nx, ny, ox, oy)
        key = (dres, -dop, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]