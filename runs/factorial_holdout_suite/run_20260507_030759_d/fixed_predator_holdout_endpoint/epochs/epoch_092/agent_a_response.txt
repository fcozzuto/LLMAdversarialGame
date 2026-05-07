def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def move_toward(tx, ty):
        best = (10**9, None, None)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not in_bounds(nx, ny):
                    continue
                d = cheb(nx, ny, tx, ty)
                if d < best[0] or (d == best[0] and (dx, dy) == (0, 0) and best[1] != (0, 0)):
                    best = (d, dx, dy)
        if best[1] is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    if (sx, sy) in resources:
        return [0, 0]

    # Resource target selection:
    # Prefer resources where we are not slower than opponent, maximizing our time advantage;
    # if none, go for the closest (in Chebyshev) resource to pressure before being denied.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd == 0:
            key = (1, 9999, -sd, -rx, -ry)
        else:
            advantage = od - sd  # positive means we can arrive no later
            key = (1 if sd <= od else 0, advantage, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    return move_toward(rx, ry)