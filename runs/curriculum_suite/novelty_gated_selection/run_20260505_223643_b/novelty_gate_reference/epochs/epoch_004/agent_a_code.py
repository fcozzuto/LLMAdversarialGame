def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs)

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_sc = -10**18
        for rx, ry in resources:
            myd = cd(x, y, rx, ry)
            opd = cd(ox, oy, rx, ry)
            sc = 10 * (opd - myd) - myd
            if sc > best_sc:
                best_sc = sc
                best_r = (rx, ry)
        tx, ty = best_r
        best_move = [0, 0]
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            myd = cd(nx, ny, tx, ty)
            opd = cd(ox, oy, tx, ty)
            sc = 10 * (opd - myd) - myd - 2 * cd(nx, ny, ox, oy)
            if sc > best_val:
                best_val = sc
                best_move = [dx, dy]
        return best_move

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = cd(nx, ny, ox, oy) - 3 * cd(nx, ny, x, y)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move