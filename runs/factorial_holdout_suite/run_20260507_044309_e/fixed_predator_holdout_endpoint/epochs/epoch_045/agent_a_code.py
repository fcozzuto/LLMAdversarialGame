def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    best_key = None
    best_t = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = ((od - sd), -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    rx, ry = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)
    cur_sd = cheb(sx, sy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)
        margin = od2 - sd2
        # Prefer taking target while keeping opponent lag; break ties by closer target and position
        key = (margin, -sd2, -abs(nx - sx) - abs(ny - sy), -nx, -ny)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    # If all moves blocked, stay still deterministically
    return [int(best_move[0]), int(best_move[1])]