def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = set((x, y) for x, y in observation.get("obstacles", []))

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in role) or ("evader" in opp_role)

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sign(a):
        return 0 if a == 0 else (1 if a > 0 else -1)

    # Choose a strategic target corner deterministically
    # Pursuer tries to get to the closest corner to opponent; evader tries to get to farthest corner.
    if pursuer:
        target = min(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0], c[1]))
    else:
        target = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), -c[0], -c[1]))

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d_opp = cheb(nx, ny, ox, oy)
        d_t = cheb(nx, ny, target[0], target[1])

        if pursuer:
            # minimize distance to opponent; break ties by pushing toward target corner
            score = (-d_opp * 1000) + (-d_t)
            # small preference to move in direction of opponent to avoid oscillation
            score += (sign(nx - sx) * sign(ox - sx) + sign(ny - sy) * sign(oy - sy)) * 2
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # maximize distance to opponent; break ties by pushing toward target corner
            score = (d_opp * 1000) + (-d_t)
            # wall-runish: bias moves that increase separation along x/y away from opponent toward target side
            ax = sign(target[0] - ox)
            ay = sign(target[1] - oy)
            score += (sign(nx - ox) * ax + sign(ny - oy) * ay) * 2
            if best_score is None or score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]