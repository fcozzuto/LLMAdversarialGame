def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target resource: maximize opponent advantage over me (prefer resources where I'm closer).
    best_t = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Primary: how much closer I am than opponent. Secondary: closer overall.
        score = (opd - myd) * 200 - myd
        if (rx + ry) < (w + h - 2) and (rx + ry) > 0:
            score += 3  # tiny tie-break away from extremes
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose one-step move that improves my distance to target and (slightly) worsens opponent distance.
    best_move = (0, 0)
    best_move_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)
        # If we step onto a resource, prioritize heavily.
        pick = 35 if (nx, ny) == (rx, ry) else 0
        # Also, if this move increases distance too much, penalize.
        immediate = (cheb(sx, sy, rx, ry) - myd2) * 50
        # Small deterministic tie-break favoring moves that drift toward our corner (agent_b usually starts at opposite corner).
        corner_bias = -abs((nx + ny) - (w + h - 2))
        score = pick + immediate + (opd2 - myd2) * 5 + corner_bias
        if score > best_move_score:
            best_move_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]