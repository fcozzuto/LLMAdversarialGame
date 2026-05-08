def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = w // 2, h // 2
    target = (cx, cy)
    best = None
    if resources:
        best_key = None
        for rx, ry in resources:
            myd = dist8(sx, sy, rx, ry)
            opd = dist8(ox, oy, rx, ry)
            key = (opd - myd, -myd, rx + ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        target = best if best is not None else (cx, cy)

        if any(dist8(sx, sy, rx, ry) <= dist8(ox, oy, rx, ry) for rx, ry in resources):
            nearest_win = None
            nearest_d = None
            for rx, ry in resources:
                myd = dist8(sx, sy, rx, ry)
                opd = dist8(ox, oy, rx, ry)
                if myd <= opd:
                    if nearest_d is None or myd < nearest_d or (myd == nearest_d and (rx + ry) < (nearest_win[0] + nearest_win[1])):
                        nearest_d = myd
                        nearest_win = (rx, ry)
            if nearest_win is not None:
                target = nearest_win

    tx, ty = target
    best_move = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist8(nx, ny, tx, ty)
        key = (d, dx * 0 + dy * 0)
        if best_d is None or key < (best_d, 0):
            best_d = d
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]