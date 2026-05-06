def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Denial-aware greedy: prefer moves that reduce (d_to_resource - d_to_opponent)
    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Evaluate the best resource target under "race pressure"
        local_best = None
        for tx, ty in res:
            dme = max(0, man((nx, ny), (tx, ty)))
            dop = max(0, man((ox, oy), (tx, ty)))
            score = dme - dop  # lower is better; negative means we are closer than opponent
            # slight preference for nearer resources overall once race pressure is similar
            score2 = score * 10 + dme
            if local_best is None or score2 < local_best:
                local_best = score2
        if local_best is None:
            continue

        # Small bias toward moving generally away from opponent when race is unclear
        dash = man((nx, ny), (ox, oy))
        val = (local_best, -dash)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]