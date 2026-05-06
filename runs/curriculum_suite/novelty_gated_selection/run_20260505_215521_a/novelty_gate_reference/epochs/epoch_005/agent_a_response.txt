def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def step_pos(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    cx, cy = w // 2, h // 2

    if not resources:
        best = (0, 0)
        best_score = -10**18
        for dx, dy in deltas:
            nx, ny = step_pos(dx, dy)
            if (nx, ny) != (sx, sy) or (dx, dy) == (0, 0):
                score = -cheb(nx, ny, cx, cy) + 0.25 * cheb(nx, ny, ox, oy)
                if score > best_score:
                    best_score = score
                    best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = step_pos(dx, dy)
        my_to_center = cheb(nx, ny, cx, cy)
        score = -0.06 * my_to_center  # mild center control
        # Resource-focused evaluation with "resource_denier" awareness:
        # Prefer resources we can reach sooner; penalize those where opponent is closer.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            diff = opd - myd
            if diff > 0:
                score += 3.2 / (1 + myd) + 0.25 * diff  # seizeable
            elif diff < 0:
                score -= 2.1 / (1 + myd) + 0.35 * (-diff)  # likely denied
            else:
                score += 0.2 / (1 + myd)  # contested
            # Deny by approaching resources where opponent is close but we aren't winning:
            if opd <= 2 and myd > opd:
                score -= 0.9 * (myd - opd)
        # Secondary avoidance: discourage moving into immediate proximity of opponent
        score += 0.10 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]