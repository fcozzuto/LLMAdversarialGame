def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, tx, ty) + 0.05 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dxm, dym]
        return best

    best_target = None
    best_tv = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # Prefer targets where we are closer than opponent, and also avoid being too far.
        tv = (-d_me) + 0.35 * d_op - 0.02 * (abs(rx - (w - 1) // 2) + abs(ry - (h - 1) // 2))
        if tv > best_tv:
            best_tv = tv
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = [0, 0]
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_me = cheb(nx, ny, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        # After moving, prioritize decreasing our distance; also slightly penalize moves that let opponent be closer.
        val = (-d_me) + 0.55 * d_op - 0.06 * cheb(nx, ny, ox, oy) + 0.01 * (dxm == 0 and dym == 0)
        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move