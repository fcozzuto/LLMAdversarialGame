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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                resources.append((rx, ry))

    if resources:
        best = (0, 0)
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            move_val = -0.5 * cheb(nx, ny, sx, sy)
            for tx, ty in resources:
                d_us = cheb(nx, ny, tx, ty)
                d_op = cheb(ox, oy, tx, ty)
                advantage = d_op - d_us  # positive means we are closer
                if (tx == nx and ty == ny):
                    advantage += 50
                move_val += 3.0 * advantage - 0.15 * d_us
            if move_val > best_val:
                best_val = move_val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    bx, by = 0, 0
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = -cheb(nx, ny, cx, cy)
        if val > best_val:
            best_val = val
            bx, by = dx, dy
    return [int(bx), int(by)]