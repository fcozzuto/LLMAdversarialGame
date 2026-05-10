def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = w - 1, h - 1
        if (sx + 1) < w: tx = w // 2
        if sx > w // 2: tx = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Pick best target resource based on "who arrives first", tie-breaking by closeness.
    best_t = None
    best_val = -10**9
    for rx, ry in resources:
        d_me = dist8(sx, sy, rx, ry)
        d_opp = dist8(ox, oy, rx, ry)
        val = (d_opp - d_me) * 1000 + (d_opp - d_me >= 0) * 200 + (15 - d_me)
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t
    # Choose move that best advances toward target while denying opponent.
    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_me = dist8(nx, ny, tx, ty)
        d_opp = dist8(ox, oy, tx, ty)
        # Prefer reducing our distance; also prefer states where we get relatively closer than opponent.
        score = -d_me * 50 + (d_opp - d_me) * 80

        # Add small "resource denying" term: avoid stepping toward a different resource where opponent is closer.
        deny = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            dm2 = dist8(nx, ny, rx, ry)
            do2 = dist8(ox, oy, rx, ry)
            if do2 + 0 <= dm2:
                deny += 1
        score -= deny * 200

        # Deterministic tie-break: prefer staying toward diagonals? Use lexicographic on move.
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move