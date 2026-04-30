def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def risk(x, y):
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    r += 2.0
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            r += 0.15
        return r

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        # Drift away from obstacles and toward center-ish, while avoiding opponent if close.
        best = None
        bestv = 10**18
        ccx, ccy = w // 2, h // 2
        for dx, dy, nx, ny in valid:
            v = cheb(nx, ny, ccx, ccy) + 0.6 * risk(nx, ny) + 0.15 * cheb(nx, ny, ox, oy)
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes "resource advantage" while keeping low risk.
    # Smaller target cost is better for us.
    best_move = (0, 0)
    best_cost = 10**18
    alpha = 1.3  # risk weight
    beta = 1.0   # opponent-advantage weight
    for dx, dy, nx, ny in valid:
        # Evaluate best resource from the candidate next position
        local_best = 10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we are not behind; penalize being behind.
            behind = d_opp - d_self
            opp_pen = behind if behind > 0 else 0.0
            cost = d_self + alpha * risk(nx, ny) + beta * opp_pen
            if cost < local_best:
                local_best = cost
        # Small deterministic tie-break: prefer moves closer to some resource and away from obstacles
        if local_best < best_cost:
            best_cost = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]