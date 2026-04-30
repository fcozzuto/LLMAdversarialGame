def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # If no resources visible, drift toward center while staying safe
    if not resources:
        tx, ty = (w // 2, h // 2)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            cand = (-(d), -cheb(nx, ny, ox, oy), dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[2], best[3]] if best else [0, 0]

    # Compete for the best resource: prefer moves that put us closer than opponent
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate best single target resource
        local_best = None
        for rx, ry in resources:
            d_you = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # High priority: reduce distance; extra reward if we are closer than opponent
            score = (1000 - 30 * d_you) + (40 * (d_op - d_you))
            # Slight prefer pulling toward center to avoid edge trapping late
            cx, cy = w // 2, h // 2
            score -= 2 * cheb(nx, ny, cx, cy)

            if local_best is None or score > local_best:
                local_best = score

        # Tie-break: keep distance from opponent unless it helps scoring already
        tie = -cheb(nx, ny, ox, oy)
        cand = (local_best, tie, -dx, -dy, dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    return best_move if ok(sx + best_move[0], sy + best_move[1]) else [0, 0]