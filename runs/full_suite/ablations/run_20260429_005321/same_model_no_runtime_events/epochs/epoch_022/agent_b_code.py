def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_t = None
    best_v = -10**18
    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer targets where we have an advantage (opponent farther), then closer.
        v = (od - sd) * 100 - sd
        # Deterministic tie-break by position
        if v > best_v or (v == best_v and (x, y) < best_t):
            best_v = v
            best_t = (x, y)

    if best_t is None:
        # No visible resources: move to maximize distance from opponent
        tx, ty = ox, oy
        best_d = -1
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d > best_d or (d == best_d and (dx, dy) < best_move):
                    best_d = d
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = best_t
    best_dist = 10**9
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            d = cheb(nx, ny, tx, ty)
            if d < best_dist or (d == best_dist and (dx, dy) < best_move):
                best_dist = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]