def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Predict opponent's current collection target (closest by Chebyshev).
    target = None
    best_od = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = cheb(ox, oy, rx, ry)
        if best_od is None or d < best_od or (d == best_od and (rx, ry) < target):
            best_od = d
            target = (rx, ry)

    if target is None:
        return [0, 0]
    tx, ty = target

    # Intercept: move to maximize being closer to opponent's target than the opponent is.
    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_d = cheb(nx, ny, tx, ty)
        opp_d = best_od
        adv = opp_d - self_d  # positive if we can reach/block sooner
        # Secondary: if we can steal any other resource, slightly prefer it.
        steal = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if cheb(nx, ny, rx, ry) < cheb(ox, oy, rx, ry):
                steal = 1
                break
        score = adv + (0.25 if steal else 0.0) - 0.02 * self_d
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]