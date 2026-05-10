def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_key = (-10**18, -10**18, -10**18)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; otherwise take ones that deny them.
        key = (od - sd, -sd, od)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    best_mv = (0, 0)
    best_mv_key = (-10**18, -10**18, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = cheb(nx, ny, tx, ty)
        # Small adversarial bias: prefer moves that also increase their distance to our target.
        od2 = cheb(ox, oy, tx, ty)
        progress = cheb(sx, sy, tx, ty) - sd2
        key = (progress, -sd2, od2)
        if key > best_mv_key:
            best_mv_key = key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]