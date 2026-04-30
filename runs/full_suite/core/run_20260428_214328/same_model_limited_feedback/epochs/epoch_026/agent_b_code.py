def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    # Candidate moves in deterministic order (prefers staying if equally good)
    moves = [[0, 0], [0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose target: prioritize resources where we are closer than opponent
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist2((sx, sy), (rx, ry))
            opd = dist2((ox, oy), (rx, ry))
            # Lower is better: weighted advantage, slightly favor nearer resources
            val = (myd - 0.85 * opd) + 0.01 * (myd)
            if best is None or val < best[0] or (val == best[0] and (rx, ry) < best[1]):
                best = (val, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)
    else:
        tx, ty = (w // 2, h // 2)

    # Pick move minimizing distance to target while avoiding obstacles/out of bounds
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d = dist2((nx, ny), (tx, ty))
        # slight tie-break: prefer moves that also keep distance from opponent
        od = dist2((nx, ny), (ox, oy))
        val = d - 0.02 * od
        if best_val is None or val < best_val or (val == best_val and [dx, dy] < best_move):
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]