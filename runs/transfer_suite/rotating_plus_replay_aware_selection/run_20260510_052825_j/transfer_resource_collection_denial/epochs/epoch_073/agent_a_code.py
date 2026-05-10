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

    if not resources:
        return [0, 0]

    best_res = None
    best_key = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Maximize our advantage; tie-break closer to us, then farther from opponent, then coordinates.
        key = (-(od - sd), sd, -od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]

    tx, ty = best_res
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    # If we can capture a resource now, take it deterministically.
    for rx, ry in resources:
        if (sx, sy) == (rx, ry) and legal(sx, sy):
            return [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # Prefer moves that increase (od - sd); if equal, minimize sd; then prefer blocking (maximize opponent distance to target).
        # Finally tie-break by (dx,dy) to remain deterministic.
        key = (-(nod - nsd), nsd, -nod, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If all moves were illegal (shouldn't happen), stay put.
    return [int(best_move[0]), int(best_move[1])]