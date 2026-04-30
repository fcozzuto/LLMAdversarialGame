def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        # No resources visible: drift toward center while keeping distance from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        options = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = None
        for dx, dy in options:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                dcen = abs(nx - cx) + abs(ny - cy)
                dop = abs(nx - ox) + abs(ny - oy)
                key = (dcen, -dop, dx, dy)
                if best is None or key < best[0]:
                    best = (key, (dx, dy))
        return list(best[1]) if best else [0, 0]

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a resource with priority for which we are relatively closer
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d1 = abs(rx - sx) + abs(ry - sy)
        d2 = abs(rx - ox) + abs(ry - oy)
        # Smaller is better; slight bias toward closer and slightly away from opponent
        key = (d1 - 0.6 * d2, d1, -d2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    tx, ty = best_res
    options = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = None
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dcur = abs(sx - tx) + abs(sy - ty)
        dnext = abs(nx - tx) + abs(ny - ty)
        dop_next = abs(nx - ox) + abs(ny - oy)
        # Prefer shortest progress to target; tie-break by staying away from opponent and deterministically by move
        key = (dnext, -dop_next, -(dcur - dnext), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return list(best[1]) if best else [0, 0]