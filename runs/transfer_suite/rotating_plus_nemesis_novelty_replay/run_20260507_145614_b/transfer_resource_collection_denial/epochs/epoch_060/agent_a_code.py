def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx, ty = w - 1, h - 1
        if sx < tx:
            sx_dir = 1
        elif sx > tx:
            sx_dir = -1
        else:
            sx_dir = 0
        if sy < ty:
            sy_dir = 1
        elif sy > ty:
            sy_dir = -1
        else:
            sy_dir = 0
        return [sx_dir, sy_dir]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in map(tuple, resources):
        return [0, 0]

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        cur_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we can arrive much earlier than opponent.
            val = (od - sd) * 1000 - sd * 2 + (1 if sd == 0 else 0)
            if val > cur_best:
                cur_best = val
        if cur_best > best_val:
            best_val = cur_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]