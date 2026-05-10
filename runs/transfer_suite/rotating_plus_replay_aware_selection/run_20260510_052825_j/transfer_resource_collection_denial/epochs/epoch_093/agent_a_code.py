def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def best_resource():
        best = None
        best_key = None
        any_close = False
        for rx, ry in resources:
            if not legal(rx, ry):
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd <= od:
                any_close = True
            # Key: prefer resources we can reach no later than opponent; among them, maximize (od-sd)
            gap = od - sd
            key = (0 if sd <= od else 1, -(gap), sd, od, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        if best is not None:
            return best
        return resources[0]

    tx, ty = best_resource()

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # Prefer minimizing our distance; if tied, increase opponent's relative slowness; then prefer staying closer to center (tie-break).
        center_bias = abs((w - 1) / 2 - nx) + abs((h - 1) / 2 - ny)
        key = (sd2, -(od2 - sd2), center_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If every move was illegal (rare), fall back to staying put.
    if not legal(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]