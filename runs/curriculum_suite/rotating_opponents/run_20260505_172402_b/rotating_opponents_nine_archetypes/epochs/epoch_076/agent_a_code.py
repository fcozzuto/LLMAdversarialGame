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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    # Strategic change: contest resources by maximizing (op_dist - my_dist), but also add a mild "interceptor" bias.
    best_target = None
    best_key = (-10**18, 10**18, 10**18)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # interceptor-ish: prefer targets that are "in front" of opponent toward center-ish
        center_bias = -cheb(rx, ry, (w - 1) // 2, (h - 1) // 2)
        key = (opd - myd, center_bias, -myd)
        if key > (best_key[0], best_key[1], best_key[2]):
            best_key = (key[0], key[1], key[2])
            best_target = (rx, ry)

    if best_target is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_target

    # Greedy step to target; if blocked, pick best valid alternative.
    best_move = (0, 0)
    best_val = (-10**18, 10**18, 10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # prefer smaller distance to target, then prefer moves that reduce opponent potential slightly (tie-break)
        val = (-myd2, -opd2, -(dx * dx + dy * dy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]