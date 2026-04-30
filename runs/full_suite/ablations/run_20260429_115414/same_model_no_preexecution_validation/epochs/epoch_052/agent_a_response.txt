def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) - 0.01 * cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target that we are relatively closer to than opponent.
    best_t = resources[0]
    best_key = None
    for (rx, ry) in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Tie-break deterministically: prefer smaller our_d, then lexicographic.
        key = (opp_d - our_d, -our_d, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # Step selection: move toward target, avoid opponent proximity, and "block" by moving to reduce opp access.
    best_move = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_to = cheb(nx, ny, tx, ty)
        opp_to = cheb(ox, oy, tx, ty)
        # If we would be closer to target than opponent, that's strong.
        advantage = opp_to - our_to
        # Discourage stepping adjacent to opponent (gives them safer routes).
        opp_dist = cheb(nx, ny, ox, oy)
        near_pen = 0
        if opp_dist <= 1:
            near_pen = 50 - 10 * opp_dist
        # Small obstacle-free incentive toward target + mild tie-break by lexicographic move order.
        v = 1000 * advantage - our_to - near_pen + 0.001 * (dx + 2 * dy)
        # Deterministic tie-break: prefer smaller our_to, then smaller dx, then smaller dy
        if v > bestv:
            bestv = v
            best_move = (dx, dy)
        elif v == bestv:
            cur_to = cheb(sx + best_move[0], sy + best_move[1], tx, ty)
            if our_to < cur_to or (our_to == cur_to and (dx, dy) < best_move):
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]