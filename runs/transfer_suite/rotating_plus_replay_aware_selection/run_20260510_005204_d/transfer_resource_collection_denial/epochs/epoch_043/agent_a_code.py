def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose target resource: maximize opponent advantage to arrive first, then minimize own distance,
    # then prefer resources nearer to the opposite corner (stays competitive vs sweepers).
    best_r = None
    best_key = None
    opp_corner_bias = (w - 1 - ox) + (h - 1 - oy)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, -(abs(rx - (w - 1)) + abs(ry - (h - 1))), -(rx + 2 * ry) + 0.01 * opp_corner_bias)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Small obstacle-aware tie-break: penalize moves that reduce reachable freedom by stepping next to obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        adv = opd2 - myd2

        # adjacency penalty (deterministic, local)
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if 0 <= px < w and 0 <= py < h and (px, py) in obstacles:
                    adj += 1

        centerish = -(abs(nx - (w - 1)) + abs(ny - (h - 1)))
        val = (adv, -myd2, centerish, -adj, -(dx * dx + dy * dy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move