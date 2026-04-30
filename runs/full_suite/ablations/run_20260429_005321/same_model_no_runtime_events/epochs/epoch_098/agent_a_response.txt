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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_res = None
    best_val = -10**18
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        # Prefer resources we can arrive no later than the opponent, strongly.
        val = (d2 - d1) * 20 - d1
        if val > best_val:
            best_val = val
            best_res = (rx, ry)

    # If we can't beat anyone, switch to: maximize opponent distance while still biasing toward nearest resource.
    target = best_res
    if target is None or best_val < 0:
        # pick nearest resource for fallback
        td = 10**9
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            if d1 < td:
                td = d1
                target = (rx, ry)

    tx, ty = (target if target is not None else (sx, sy))
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # immediate resource capture
        cap = 1 if (nx, ny) in resources else 0
        d_my = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        # tactical: discourage giving opponent easy access to that target
        d_op_to_t = cheb(ox, oy, tx, ty)
        score = cap * 10000 - d_my * 3 + d_op * 0.8
        score += (d_op_to_t - d_my) * 2.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]