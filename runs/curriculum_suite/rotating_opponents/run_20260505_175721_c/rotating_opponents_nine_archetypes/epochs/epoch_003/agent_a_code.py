def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    resources = observation.get("resources", []) or []

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            key = (-(opd - myd), myd, rx, ry)  # prefer larger advantage, then closer
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            d_to_t = dist(nx, ny, tx, ty)
            d_to_o = dist(nx, ny, ox, oy)
            val = (d_to_t, -d_to_o, nx, ny)  # closest to target, then farther from opponent
            if best_val is None or val < best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move