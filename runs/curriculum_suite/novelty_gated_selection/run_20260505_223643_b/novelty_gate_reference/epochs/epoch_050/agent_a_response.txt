def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        # drift to center to avoid being static vs center_rush
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not step_ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Center-denial: choose move that most favors a resource where we can arrive earlier than opponent,
    # while discouraging approaching resources the opponent is closer to.
    best = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        our_best = 10**18
        for rx, ry in resources:
            od = cheb(ox, oy, rx, ry)
            nd = cheb(nx, ny, rx, ry)
            # Lower is better: prioritize small nd, penalize targets where opponent is nearer.
            score = nd - 0.65 * od
            # Small bonus toward being near opponent (intercept) only if we are already competitive.
            if nd <= od:
                score -= 0.05 * cheb(nx, ny, ox, oy)
            if score < our_best:
                our_best = score
        # Tie-break: prefer not getting too close to opponent if we are not competitive.
        opp_close = cheb(nx, ny, ox, oy)
        key = (our_best, -opp_close, dx, dy)
        if key < best:
            best = key

    return [best[2], best[3]]