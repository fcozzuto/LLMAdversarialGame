def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (None, None))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []) if isinstance(p, (list, tuple)) and len(p) == 2)
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            res.append((r[0], r[1]))
    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best, bestd = -10**18, (0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles: 
                    continue
                sc = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
                if sc > best:
                    best, bestd = sc, (dx, dy)
        return [bestd[0], bestd[1]]

    opp_exists = ox is not None and oy is not None
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    my_resources_set = set(res)

    best, bestd = -10**18, (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        immediate = 1.0 if (nx, ny) in my_resources_set else 0.0

        # Evaluate denial-oriented gain on the best resource after this step
        gap_best = -10**18
        dist_best = 10**18
        for rx, ry in res:
            sd = abs(rx - nx) + abs(ry - ny)
            if opp_exists:
                od = abs(rx - ox) + abs(ry - oy)
                gap = (od - sd)  # positive means we are closer than opponent to that resource
            else:
                gap = -sd
            if gap > gap_best:
                gap_best = gap
                dist_best = sd
        # Combine: prioritize being closer than opponent, then closeness, then immediate collection
        sc = 5.0 * gap_best - 0.6 * dist_best + 2.0 * immediate - 0.02 * (nx * nx + ny * ny)
        if sc > best:
            best, bestd = sc, (dx, dy)

    return [bestd[0], bestd[1]]