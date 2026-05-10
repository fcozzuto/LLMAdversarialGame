def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Best resource to "race" from this next position.
        best_r_adv = None
        best_r_dist = None
        best_r_tieb = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer than opponent
            dist_tieb = myd
            # Deterministic tie-break: prefer closer, then prefer larger coordinates (stable).
            tieb = (-dist_tieb, -(rx * 100 + ry))
            if best_r_adv is None or (adv, tieb) > (best_r_adv, best_r_tieb):
                best_r_adv = adv
                best_r_dist = myd
                best_r_tieb = tieb

        # Move score: maximize winning pressure, then minimize distance to that resource,
        # and lastly add a small bias toward the grid center to avoid dithering.
        center_bias = -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0)
        score = (best_r_adv, -best_r_dist, center_bias, -(dx * dx + dy * dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]