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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-(10**18), (0, 0))
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -cheb(nx, ny, cx, cy)
            if score > best[0]:
                best = (score, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    best_score = -(10**18)
    best_move = (0, 0)

    # Score a move by: how quickly we reach resources vs opponent, plus mild tie-breakers.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        move_score = 0
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Encourage contested/improving captures: win distance and get closer.
            # Higher when we are closer than opponent; still values progress when behind.
            rel = d_opp - d_self  # positive is good
            move_score += (rel * 10) - d_self

            # If we land on a resource, strongly prioritize.
            if nx == rx and ny == ry:
                move_score += 500

        # Prefer staying on-board and not drifting into dead corners when close.
        # Also add small bias to reduce distance to opponent when resources are scarce.
        if len(resources) <= 4:
            move_score -= cheb(nx, ny, ox, oy) * 0.5

        if move_score > best_score:
            best_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]