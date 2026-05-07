def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Counter sweep_rows: prefer resources in rows less aligned with opponent
        bias = 0.15 * abs(ry - oy) - 0.05 * abs(rx - ox)
        key = (do - ds + bias, -ds, -abs(rx - sx) - abs(ry - sy), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Encourage taking lead while staying on a direct path
        step_key = (od - nd, -nd, -abs(tx - nx) - abs(ty - ny), -dx, -dy)
        if best_step_key is None or step_key > best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]