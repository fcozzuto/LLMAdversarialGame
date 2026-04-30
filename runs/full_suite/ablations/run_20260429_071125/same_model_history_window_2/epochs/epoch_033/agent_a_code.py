def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If fewer resources remain, we can afford greedier play; otherwise prioritize contested resources.
    rc = int(observation.get("remaining_resource_count", len(resources)) or 0)
    aggressive = 1 if rc <= 4 else 0

    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Base: stay closer to opponent to reduce their safe collection routes slightly.
        # Deterministic tie-breaking uses dx,dy ordering from moves list.
        my_opp_dist = cheb(nx, ny, ox, oy)
        val = -0.01 * my_opp_dist

        # Target selection: maximize (opp_dist - my_dist) toward a resource,
        # encouraging moves that put us closer than the opponent.
        if resources:
            local_best = -10**18
            for rx, ry in resources:
                if (rx, ry) == (nx, ny):
                    local_best = 10**6  # immediate pickup
                    break
                d_my = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                lead = d_op - d_my  # positive if we are closer than opponent
                # Prefer closer resources; contested resources matter more.
                contest_weight = 1.0 if aggressive else 1.8
                score = contest_weight * lead - 0.35 * d_my + (0.02 * d_op)
                # Slight preference for resources closer to center to reduce corner-locked dead ends.
                cx, cy = w // 2, h // 2
                center_bias = -0.01 * cheb(rx, ry, cx, cy)
                score += center_bias
                if score > local_best:
                    local_best = score
            val += local_best

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]