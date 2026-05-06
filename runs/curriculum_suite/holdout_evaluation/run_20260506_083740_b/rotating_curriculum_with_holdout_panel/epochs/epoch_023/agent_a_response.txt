def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        # Deterministic sweep to opposite corner from start bias using both axes
        tx = w - 1 if sx < w - 1 - sx else 0
        ty = h - 1 if sy < h - 1 - sy else 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]

    # Choose a target where we have the largest arrival advantage (opp farther than us).
    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Also penalize targets that are "too close" to opponent (likely contested)
        contested_pen = 0 if od - sd > 1 else -(2 - (od - sd))
        val = (od - sd) * 10 + contested_pen - sd * 0.1 + (rx * 0.01 + ry * 0.001)
        if val > best_val:
            best_val = val
            best_t = (rx, ry)

    rx, ry = best_t
    # Among next moves, pick the one maximizing advantage and reducing opponent access.
    best_move = (0, 0)
    best_score = -10**18
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        sd2 = man(nx, ny, rx, ry)
        od2 = man(ox, oy, rx, ry)  # opponent move unknown; use current access
        # Encourage breaking ties in our favor and not letting opponent become closer
        score = (od2 - sd2) * 10 - sd2 * 0.2
        score += (1 if (nx, ny) == (rx, ry) else 0) * 1000
        # Light preference to align toward target
        score += -abs((nx - sx) - (rx - sx) / (abs(rx - sx) + 1e-9)) * 0  # deterministic no-op
        if score > best_score:
            best_score = score
            best_move = (mdx, mdy)

    if valid(sx + best_move[0], sy + best_move[1]):
        return [best_move[0], best_move[1]]

    # Fallback: any valid move that doesn't collide
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if valid(nx, ny):
            return [mdx, mdy]
    return [0, 0]