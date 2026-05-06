def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_move_for_target(tx, ty):
        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            val = (opd - myd, -myd, -cheb(nx, ny, ox, oy))
            if best is None or val > best_val:
                best = [dx, dy]
                best_val = val
        return best

    valid_targets = [(rx, ry) for (rx, ry) in resources if inb(rx, ry) and (rx, ry) not in obstacles]
    if valid_targets:
        best_t = None
        best_t_val = None
        for tx, ty in valid_targets:
            myd = cheb(sx, sy, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            val = (opd - myd, -myd, -cheb(sx, sy, ox, oy))
            if best_t is None or val > best_t_val:
                best_t = (tx, ty)
                best_t_val = val
        mv = best_move_for_target(best_t[0], best_t[1])
        if mv is not None:
            return mv

    # Fallback: move to maximize distance from opponent
    best = None
    best_d = -1
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, ox, oy)
        if d > best_d:
            best_d = d
            best = [dx, dy]
    return best if best is not None else [0, 0]