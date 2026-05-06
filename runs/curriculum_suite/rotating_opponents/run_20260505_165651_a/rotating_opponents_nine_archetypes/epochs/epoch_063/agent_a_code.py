def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources") or []

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        if resources:
            d_res = 10**9
            for r in resources:
                rx, ry = r[0], r[1]
                t = man(nx, ny, rx, ry)
                if t < d_res:
                    d_res = t
        else:
            d_res = man(nx, ny, cx, cy)
        key = (d_opp, -d_res, -abs(dx) - abs(dy))
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]