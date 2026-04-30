def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    def opp_min_dist_to_target(tx, ty):
        best = 10**9
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < best:
                    best = d
        return best if best != 10**9 else cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = 10**18
    beta = 0.7

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            cur = 10**18
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = opp_min_dist_to_target(rx, ry)
                v = my_d - beta * op_d
                if v < cur:
                    cur = v
            if cur < best_val:
                best_val = cur
                best_move = (dx, dy)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best_val:
                best_val = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]