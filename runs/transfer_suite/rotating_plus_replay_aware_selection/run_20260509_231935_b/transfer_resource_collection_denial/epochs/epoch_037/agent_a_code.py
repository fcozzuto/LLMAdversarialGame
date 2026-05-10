def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources_list:
        return [0, 0]

    res = set((p[0], p[1]) for p in resources_list)
    obs = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup if possible
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    # Pick target resource: maximize advantage (opponent slower than us), then prefer closer
    best = None
    for rx, ry in res:
        if (rx, ry) in obs:
            continue
        sd = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + 3 * ry))
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]

    # Choose move that improves competitive advantage toward target; avoid obstacles
    best_m = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = dist8(nx, ny, tx, ty)
        # approximate opponent reaction by assuming we care about relative distance
        od = dist8(ox, oy, tx, ty)
        # strong reward if we land on any resource (including target)
        pickup = 1.0 if (nx, ny) in res else 0.0
        val = ((od - sd2), -sd2, pickup, -(abs(nx - tx) + abs(ny - ty)))
        if best_m is None or val > best_m[0]:
            best_m = (val, (dx, dy))

    return list(best_m[1]) if best_m is not None else [0, 0]