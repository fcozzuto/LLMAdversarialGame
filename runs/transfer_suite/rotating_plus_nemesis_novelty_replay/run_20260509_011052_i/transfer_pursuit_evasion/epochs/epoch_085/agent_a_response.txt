def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def best_corner_bias(px, py, prefer_far):
        # prefer_far=True => maximize distance to px,py from (px,py); otherwise minimize
        best = corners[0]
        bd = cheb(px, py, best[0], best[1])
        for cx, cy in corners[1:]:
            d = cheb(px, py, cx, cy)
            if (d > bd) if prefer_far else (d < bd):
                bd, best = d, (cx, cy)
        return cheb(px, py, best[0], best[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Heuristic: chase/evade by chebyshev distance; add obstacle-aware corner bias; deterministic tie-break by fixed dir order.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        corner_dist = best_corner_bias(nx, ny, prefer_far=not is_pursuer)
        # Pursuer wants small d; evader wants large d. Corner_dist encourages moving between corners deterministically.
        val = (-d if is_pursuer else d) + (0.03 * corner_dist if is_pursuer else 0.03 * corner_dist)
        # Small preference to keep closer to center when scores tie (deterministic, robustness against corner traps)
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        center_pen = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) / (w * h)
        val += 1e-4 * center_pen
        if best_val is None or (val > best_val if not is_pursuer else val > best_val):
            best_val = val
            best_move = (dx, dy)

    # Fallback if all invalid (shouldn't happen with staying put allowed unless blocked by obstacle at current, which should be impossible)
    if best_move == (0, 0) and not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]