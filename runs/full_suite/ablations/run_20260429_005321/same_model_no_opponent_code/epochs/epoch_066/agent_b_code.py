def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Choose a target resource we can reach relatively better than the opponent.
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        our = d2(sx, sy, rx, ry)
        opp = d2(ox, oy, rx, ry)
        # Prefer being closer than opponent; also prefer closer absolute when similar advantage.
        val = (opp - our) * 10 - our
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    # If no resources visible, drift toward opponent corner to keep pressure.
    if best_t is None:
        target_x, target_y = 0 if ox >= w // 2 else w - 1, 0 if oy >= h // 2 else h - 1
    else:
        target_x, target_y = best_t

    # Pick move that reduces distance to target, with obstacle-near penalty and deterministic tie-break.
    def obstacle_near(nx, ny):
        cnt = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    cnt += 1
        return cnt

    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        dist = d2(nx, ny, target_x, target_y)
        near_pen = obstacle_near(nx, ny)
        # also mildly discourage moving to cells closer to opponent's target if we selected one
        opp_dist_after = d2(ox, oy, target_x, target_y)
        score = (-dist) * 10 - near_pen * 3 + (opp_dist_after - dist) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]