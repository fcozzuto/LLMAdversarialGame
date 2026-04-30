def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles:
        return [0, 0]
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    t = int(observation.get("turn_index", 0) or 0)

    # Choose a target resource we can reach relatively earlier than the opponent.
    best_target = resources[0]
    best_tval = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Early contest slightly favors contesting; later slightly favors shorter routes.
        w1 = 1.2 if t < 20 else 0.9
        w2 = 0.2 if t < 20 else 0.45
        val = (opd - myd) * w1 - myd * w2
        # Deterministic tie-breaker
        if val > best_tval or (val == best_tval and (rx, ry) < best_target):
            best_tval = val
            best_target = (rx, ry)

    tx, ty = best_target

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer getting closer to target and keeping opponent from being closer next.
        val = (opd - myd)
        # Small preference for reducing total distance to the board center (stabilize routing).
        cx, cy = (w - 1) // 2, (h - 1) // 2
        val -= 0.02 * cheb(nx, ny, cx, cy)
        # Slightly discourage stepping away from target.
        curd = cheb(sx, sy, tx, ty)
        val += 0.05 * (curd - myd)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]