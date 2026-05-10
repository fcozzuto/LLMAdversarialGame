def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacle_set

    if not resources:
        return [0, 0]

    def best_value(px, py):
        best = None
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive earlier; if tied, prefer farther from opponent.
            val = (od - myd, -(myd), -(cheb(ox, oy, px, py)))
            if best is None or val > best:
                best = val
        return best[0], best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cur_val = best_value(sx, sy)
    best_mv = (0, 0)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = best_value(nx, ny)
        # Additional anti-opponent pressure: prefer being closer to where opponent currently is heading (nearest resource).
        # Deterministic "pressure" target: the resource minimizing opponent distance.
        nrx, nry, odmin = None, None, None
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            if odmin is None or od < odmin:
                odmin, nrx, nry = od, rx, ry
        press = -cheb(nx, ny, nrx, nry) if nrx is not None else 0
        key = (v[0], v[1], press, -cheb(nx, ny, ox, oy))
        if best is None or key > best:
            best = key
            best_mv = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]