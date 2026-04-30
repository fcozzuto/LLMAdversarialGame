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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Go to opponent farthest while drifting to center-ish to avoid wasting time
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy) - 0.02 * cheb(nx, ny, int(round(cx)), int(round(cy)))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Score each move by the best resource after the move, prioritizing gaining distance-advantage.
    # Deterministic tie-break: smaller (dx,dy) lexicographically.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate top target(s) only: best gain and best closeness to avoid expensive search.
        local_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Gain: positive if I'm closer than opponent.
            gain = d_op - d_me
            # Also prefer smaller absolute distance once gain is similar.
            val = 1000 * gain - d_me
            if val > local_best:
                local_best = val

        # Add mild anti-trap: prefer not to get too close to opponent (prevents giving them easier steals)
        anti = -0.05 * cheb(nx, ny, ox, oy)
        score = local_best + anti

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]