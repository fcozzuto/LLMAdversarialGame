def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    tx, ty = None, None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        key = (od - sd, -sd, -ry, -rx, sd)  # prefer where we are closer; tie-break deterministically
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    if tx is None:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = md(nx, ny, tx, ty)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < best_move):
            bestd = d
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]