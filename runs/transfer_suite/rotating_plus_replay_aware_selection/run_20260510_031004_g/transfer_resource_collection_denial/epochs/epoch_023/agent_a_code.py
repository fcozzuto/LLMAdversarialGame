def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    res = [(int(p[0]), int(p[1])) for p in resources]
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    on_resource = set(res)
    best_target = None
    best_score = None

    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        row_bias = -abs(ry - oy)  # opponent sweep_rows => contest their row first
        score = (opd - myd) * 120 + row_bias * 6 - myd
        if best_score is None or score > best_score or (score == best_score and myd < best_target[2]):
            best_score = score
            best_target = (rx, ry, myd)

    tx, ty, _ = best_target
    if not free(sx, sy):
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        val = (opd2 - myd2) * 200 - myd2
        if (nx, ny) in on_resource:
            val += 5000
        # If tied, prefer moves that reduce distance to opponent slightly (interfere with sweep)
        val -= cheb(nx, ny, ox, oy) * 1
        if best_val is None or val > best_val or (val == best_val and (abs(nx - tx) + abs(ny - ty) < abs(sx - tx) + abs(sy - ty))):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]