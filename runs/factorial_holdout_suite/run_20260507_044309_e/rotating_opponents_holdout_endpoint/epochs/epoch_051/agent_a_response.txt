def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resources.append((int(p[0]), int(p[1])))

    if not resources:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def obs_pen(x, y):
        if (x, y) in obstacles:
            return 10**6
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) in obstacles:
                    pen += 3
        return pen

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Cell scoring: favor those where we beat opponent in distance, then favor closer remaining.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        move_pen = obs_pen(nx, ny)

        # Evaluate best resource from this hypothetical position.
        cur_best = -10**18
        for rx, ry in resources:
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # If we can reach earlier (or tie), this becomes strongly positive.
            dist_gap = opp_d - self_d
            val = 1000 * dist_gap - 3 * self_d
            # Encourage targeting the closest "winning" resource.
            if dist_gap >= 0:
                val += 50
            cur_best = val if val > cur_best else cur_best

        # Slight preference for progressing away from start dead-zone and towards corners on resource scarcity.
        scarcity = observation.get("remaining_resource_count", len(resources))
        corner_bias = (abs(nx - 0) + abs(ny - 0)) if (sx <= ox and sy <= oy) else (abs(nx - (w - 1)) + abs(ny - (h - 1)))
        total = cur_best - move_pen + (-0.1 * scarcity) - 0.01 * corner_bias

        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]