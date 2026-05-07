def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_penalty(x, y):
        pen = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles: pen += 1
        return pen

    # No visible resources: head to a corner far from opponent
    if not resources:
        corners = [(0, 0), (gw - 1, 0), (0, gh - 1), (gw - 1, gh - 1)]
        tx, ty = max(corners, key=lambda c: cheb(sx, sy, c[0], c[1]) - cheb(ox, oy, c[0], c[1]))
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty) - 0.6 * obstacle_penalty(nx, ny)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Resource targeting with relative arrival advantage; prefer nearer resources and safer paths
    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        score = 0
        # Reward immediate pickup
        if (nx, ny) in obstacles:  # should not happen due to legal
            continue
        score += 1.2 if (nx, ny) in resources else 0.0

        # Find best relative advantage over opponent
        best_rel = -10**18
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Opponent slower => positive
            rel = (d_opp - d_my)
            # Tie-breaker: prefer closer absolute distance when rel is similar
            rel = rel * 2.0 - 0.15 * d_my
            if rel > best_rel:
                best_rel = rel
        score += best_rel

        # Safety: avoid moves that corner us near obstacles or get too close to opponent
        score -= 0.35 * obstacle_penalty(nx, ny)
        score -= 0.05 * cheb(nx, ny, ox, oy)

        # Deterministic tie-break: prefer smaller dx, then smaller dy, then staying still
        if score > best_val:
            best_val = score
            best_move = (dx, dy)
        elif score == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]