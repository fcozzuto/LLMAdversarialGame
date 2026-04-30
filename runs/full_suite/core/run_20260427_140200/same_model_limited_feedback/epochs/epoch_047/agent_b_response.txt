def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs = set((x, y) for x, y in obstacles)
    res = resources[:] if resources else []

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_cost(a, b):
        # Chebyshev distance for king moves
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        candidates.append((nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    if res:
        best = None
        for nx, ny, dx, dy in candidates:
            # Prefer resources where we are closer than opponent.
            best_val = None
            for rx, ry in res:
                myd = step_cost((nx, ny), (rx, ry))
                opd = step_cost((ox, oy), (rx, ry))
                val = myd - 0.45 * opd
                if best_val is None or val < best_val:
                    best_val = val
            # Small tie-breakers: prefer progress toward resources and avoid moving away.
            curd = min(step_cost((sx, sy), (rx, ry)) for rx, ry in res)
            newd = min(step_cost((nx, ny), (rx, ry)) for rx, ry in res)
            tie = (newd - curd)
            val = best_val * 1000 + tie
            if best is None or val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # No visible resources: move toward center while subtly keeping distance from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for nx, ny, dx, dy in candidates:
        dc = abs(nx - cx) + abs(ny - cy)
        do = max(abs(nx - ox), abs(ny - oy))
        val = dc * 10 - do  # slight preference for staying farther
        if best is None or val < best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]]