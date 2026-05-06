def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        for y in range(h):
            for x in range(w):
                if valid(x, y):
                    sx, sy = x, y
                    break
            else:
                continue
            break

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            local = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer resources where we are (or become) closer than opponent; also prefer being close ourselves.
                val = (opd - myd) * 20 - myd
                # Small deterministic tie-break: prefer lower coordinates.
                val += -(rx * 0.01 + ry * 0.001)
                if val > local:
                    local = val
            # Encourage reduction in our closest-resource distance to avoid dithering.
            cur_best = 10**9
            for rx, ry in resources:
                d = cheb(sx, sy, rx, ry)
                if d < cur_best:
                    cur_best = d
            new_best = 10**9
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if d < new_best:
                    new_best = d
            val2 = local + (cur_best - new_best) * 5
        else:
            # No visible resources: drift toward center away from obstacles (simple deterministic).
            cx, cy = w // 2, h // 2
            myd = cheb(nx, ny, cx, cy)
            val2 = -myd
        if val2 > best_val:
            best_val = val2
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1: dx = -1
    if dx > 1: dx = 1
    if dy < -1: dy = -1
    if dy > 1: dy = 1
    return [int(dx), int(dy)]