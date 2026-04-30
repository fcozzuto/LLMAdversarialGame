def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_pos(x, y):
        if x < 0 or y < 0 or x >= w or y >= h:
            return None
        if (x, y) in obstacles:
            return None
        return (x, y)

    # Strategy: move to position that maximizes guaranteed contesting margin.
    # Also add slight preference toward resources that are closer to opponent disadvantage.
    best_move = (0, 0)
    best_score = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if clamp_pos(nx, ny) is None:
            continue

        score = 0
        # Strongly prefer moves that bring us within 1 step of a resource
        # where we are closer than opponent.
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - our_d  # positive means we are closer
            if our_d == 0:
                score += 10000
            # contest/deny shaping
            if margin > 0:
                score += 200 * margin - 5 * our_d
            else:
                score += 0  # don't chase resources where opponent is not worse

        # If no contesting resource, move toward closest resource but avoid letting opponent close gap too much.
        if score == 0:
            # choose resource that minimizes (our distance - opponent distance)
            worst = 10**9
            for rx, ry in resources:
                val = cheb(nx, ny, rx, ry) - cheb(ox, oy, rx, ry)
                if val < worst:
                    worst = val
            score = -100 * worst - 2 * min(cheb(nx, ny, rx, ry) for rx, ry in resources)

        # Mild obstacle-aware tie-breaker: prefer staying closer to bounds center (reduces corner traps).
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        score -= int(dist_center)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]