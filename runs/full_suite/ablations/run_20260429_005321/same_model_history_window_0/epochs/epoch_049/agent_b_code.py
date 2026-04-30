def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def best_target_from(x, y):
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist2(x, y, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            priority = (opd - myd)  # higher means I'm relatively closer
            if best is None or priority > best[0] or (priority == best[0] and myd < best[1]):
                best = (priority, myd, rx, ry)
        return best

    target = best_target_from(sx, sy)

    if target is None:
        return [0, 0]

    _, _, tx, ty = target

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Base: go toward target
        myd_next = dist2(nx, ny, tx, ty)
        base = -myd_next

        # Bonus if reducing distance swing vs opponent on this move
        opd = dist2(ox, oy, tx, ty)
        rel = (opd - dist2(nx, ny, tx, ty))

        # Small penalty for being "stuck" near obstacles
        neigh_obs = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                px, py = nx + ddx, ny + ddy
                if in_bounds(px, py) and (px, py) in obstacles:
                    neigh_obs += 1
        score = base + 0.3 * rel - 0.05 * neigh_obs

        # If on a resource, prefer immediately
        if (nx, ny) in resources:
            score += 1e6

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]