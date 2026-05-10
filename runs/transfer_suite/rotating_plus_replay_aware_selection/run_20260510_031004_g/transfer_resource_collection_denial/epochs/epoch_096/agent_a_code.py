def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer resources I can reach earlier; also contest if opponent is close.
        key = (opp_d - my_d, -my_d, -(man(sx, sy, rx, ry)), -(rx + ry), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    # If landing cell is an obstacle (or out of bounds), step only in safe axis.
    nx, ny = sx + dx, sy + dy
    if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
        opts = []
        if 0 <= sx + dx < w and (sx + dx, sy) not in obstacles:
            opts.append((dx, 0))
        if 0 <= sy + dy < h and (sx, sy + dy) not in obstacles:
            opts.append((0, dy))
        if opts:
            # Deterministic: prefer axis that reduces my chebyshev distance most.
            cur = cheb(sx, sy, tx, ty)
            best_m = None
            best_mv = None
            for mx, my in opts:
                m = cheb(sx + mx, sy + my, tx, ty)
                if best_m is None or m < best_m:
                    best_m = m
                    best_mv = (mx, my)
            return [int(best_mv[0]), int(best_mv[1])]
        return [0, 0]

    return [int(dx), int(dy)]