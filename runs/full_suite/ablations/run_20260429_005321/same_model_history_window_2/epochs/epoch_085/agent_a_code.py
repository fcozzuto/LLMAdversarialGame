def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose a target resource: prefer those we reach sooner, and/or opponent reaches later.
    target = None
    best_key = None
    if resources:
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Primary: smaller (d_me - d_op). Next: smaller d_me. Next deterministic: coord.
            key = (d_me - d_op, d_me, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)
    else:
        target = (ox, oy)  # no visible resources; move toward opponent (simple pressure)

    tx, ty = target

    # One-step move: pick valid move minimizing distance to target; break ties by blocking opponent path.
    best = None
    best_key2 = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d_op_next = cheb(ox, oy, tx, ty)
        # Encourage making ourselves closer than opponent (even if opponent doesn't move this turn).
        key2 = (d1, -(d_op_next - d1), dx, dy)
        if best_key2 is None or key2 < best_key2:
            best_key2 = key2
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]