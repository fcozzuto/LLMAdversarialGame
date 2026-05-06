def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_from(px, py):
        best = None
        bestd = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            d = cheb(px, py, rx, ry)
            # tie-break to favor earlier intake-like order
            if bestd is None or d < bestd or (d == bestd and (rx + ry) < (best[0] + best[1])):
                bestd = d
                best = (rx, ry)
        return best, bestd

    # If no resources, go center-ish avoiding obstacles
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        (tx, ty), _ = best_target_from(sx, sy)
        if (tx, ty) is None:
            tx, ty = w // 2, h // 2

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = [0, 0]
    best_score = None

    # Heuristic: prioritize moving closer to our best target while maximizing opponent delay.
    # Also add repulsion from obstacles by avoiding "next-step corridors" that immediately block us.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_d = cheb(nx, ny, tx, ty)
        opp_d_to_target = cheb(ox, oy, tx, ty)

        # Opportunistic denial: if opponent is closer to the target, we try to swing toward a different resource.
        if resources and cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty):
            alt, alt_d = best_target_from(nx, ny)
            if alt is not None:
                tx2, ty2 = alt
                my_d = alt_d
                opp_d_to_target = cheb(ox, oy, tx2, ty2)

        # Obstacle pressure: if we move into a cell where many neighboring cells are blocked, penalize.
        neigh_blocked = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                px, py = nx + adx, ny + ady
                if not inb(px, py) or (px, py) in obs:
                    neigh_blocked += 1
        obstacle_pen = neigh_blocked * 0.03

        # Main score: prefer smaller my_d and larger opponent distance (resource denial effect).
        # Add a small bias to keep moving (avoid unnecessary staying).
        move_bias = 0.02 if (dx == 0 and dy == 0) else 0.0

        score = (my_d * -1.0) + (opp_d_to_target * 0.08) - obstacle_pen - move_bias

        # Deterministic tie-break: prefer lexicographically smallest move among equals.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]