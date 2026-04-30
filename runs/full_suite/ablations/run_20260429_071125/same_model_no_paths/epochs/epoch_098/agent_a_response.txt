def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in obstacles:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        # Drift toward center to avoid cornering
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        bestd = 10**9
        best = (0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny): 
                    continue
                d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                if d < bestd:
                    bestd = d
                    best = (dx, dy)
        return [int(best[0]), int(best[1])]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Targeting heuristic: maximize (opponent_distance - self_distance) for the best resource after the move.
    best_move = (0, 0)
    best_score = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        move_score = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Big preference to resources we are closer to than opponent; add slight urgency to nearer resources.
            s = (do - ds) * 10.0 - ds * 0.6
            # Tie-breaker: prefer resources closer to our line of advance toward center.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            s -= (rx - cx) * 0.03 + (ry - cy) * 0.03
            if s > move_score:
                move_score = s
        if move_score > best_score:
            best_score = move_score
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]