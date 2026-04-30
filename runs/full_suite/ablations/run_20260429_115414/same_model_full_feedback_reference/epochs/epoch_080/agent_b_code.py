def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_gap = -10**9
    # Choose resource where we have the largest time advantage (opp closer => higher opp distance? actually want opp_dist - self_dist large)
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gap = od - sd
        # Tie-breaker: prefer closer to us if gaps equal
        if gap > best_gap or (gap == best_gap and (best_target is None or sd < man(sx, sy, best_target[0], best_target[1]))):
            best_gap = gap
            best_target = (rx, ry)

    tx, ty = best_target
    # If opponent is closer (gap negative), try to intercept by heading toward the midpoint direction anyway.
    # One-step greedy: maximize (opp_dist_to_target - self_dist_after_move) with slight move tie-break toward target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        toward = -man(nx, ny, tx, ty)  # prefer smaller
        # Main: gain by reducing our distance; secondary: avoid moving to cells that increase our distance too much
        val = (od2 - sd2) * 10 + toward
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]