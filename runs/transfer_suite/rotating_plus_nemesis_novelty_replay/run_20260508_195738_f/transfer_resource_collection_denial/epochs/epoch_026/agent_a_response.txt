def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Target selection: pick a resource we can reach at least as fast as opponent; else maximize (opp_d - self_d)
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Priority: win-tight resources first; break ties by closer (lower sd), then deterministically by position
        key = ((sd <= od), (od - sd), -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        # No resources: drift to farthest corner from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (man(ox, oy, c[0], c[1]) - 0.01 * man(sx, sy, c[0], c[1]), -c[0], -c[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [int(dx), int(dy)]
        # fallback: choose any valid move that increases distance to opponent
        bestm = None
        for dx0, dy0 in moves:
            nx0, ny0 = sx + dx0, sy + dy0
            if not inb(nx0, ny0):
                continue
            val = (man(nx0, ny0, ox, oy), -man(sx, sy, nx0, ny0), -dx0, -dy0)
            if bestm is None or val > bestm[0]:
                bestm = (val, dx0, dy0)
        return [int(bestm[1]), int(bestm[2])] if bestm else [0, 0]

    _, tx, ty = best[0], best[1], best[2]
    # Greedy steering with obstacle avoidance, preferring moves that reduce self distance to target
    chosen = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # If sd2 gets smaller, prioritize; also add slight denial term to discourage stepping into opponent's faster claim
        denial = od2 - sd2
        # Deterministic tie-breakers by move vector
        val = (-sd2, -(0.05 * denial), dx * 0 + 0, -dy, -dx)
        if chosen is None or val > chosen[0]:
            chosen = (val, dx, dy)
    return [int(chosen[1]), int(chosen[2])] if chosen else [0, 0]