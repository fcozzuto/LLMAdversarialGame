def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        dx = 0
        dy = 0
        for tx, ty in [(ox, oy), (sx, sy)]:
            pass
        return [dx, dy]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    best_val = None

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        opp_d = dist2((nx, ny), (ox, oy))
        opp_pen = -0.02 * opp_d

        # Choose the resource that we are most likely to secure (ours closer than opponent)
        # and generally near to us.
        local_best = None
        for rx, ry in resources:
            ds = dist2((nx, ny), (rx, ry))
            do = dist2((ox, oy), (rx, ry))
            # Bonus for being closer; extra tie-breaking towards nearer resources.
            val = (do - ds) - 0.01 * ds
            if local_best is None or val > local_best:
                local_best = val

        val_total = local_best + opp_pen

        if best_val is None or val_total > best_val:
            best_val = val_total
            best = (dx, dy)
        elif val_total == best_val:
            # Deterministic tie-break: prefer smaller movement, then lexicographic dx,dy
            if abs(dx) + abs(dy) < abs(best[0]) + abs(best[1]):
                best = (dx, dy)
            elif abs(dx) + abs(dy) == abs(best[0]) + abs(best[1]) and (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]