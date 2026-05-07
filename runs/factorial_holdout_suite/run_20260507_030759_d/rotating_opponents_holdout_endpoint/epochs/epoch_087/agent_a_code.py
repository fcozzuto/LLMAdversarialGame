def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int) and 0 <= rx < w and 0 <= ry < h):
            continue
        if (rx, ry) in blocked:
            continue
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Prefer where we're closer; if tied, prefer closer overall.
        key = (dop - dme, -(dme + 1))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = (0, 0)
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        self_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Move to reduce our distance; break ties by improving advantage over opponent.
        key = (opp_d - self_d, -self_d, -abs(nx - tx) - abs(ny - ty))
        if best_k is None or key > best_k:
            best_k = key
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]