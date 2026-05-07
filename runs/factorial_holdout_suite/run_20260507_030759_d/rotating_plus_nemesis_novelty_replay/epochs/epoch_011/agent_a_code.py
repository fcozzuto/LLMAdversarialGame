def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    resources = [to_xy(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(to_xy(o) for o in (observation.get("obstacles", []) or []))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0:
            dx = -dx
        dy = by - ay
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return (x, y) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dir = (0, 0)
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or blocked(nx, ny):
            continue
        if resources:
            myd = 10**9
            opd = 10**9
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < myd:
                    myd = d1
                d2 = cheb(ox, oy, rx, ry)
                if d2 < opd:
                    opd = d2
            val = (opd - myd) * 10 - myd
        else:
            val = -cheb(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best_dir = (dx, dy)

    return [int(best_dir[0]), int(best_dir[1])]