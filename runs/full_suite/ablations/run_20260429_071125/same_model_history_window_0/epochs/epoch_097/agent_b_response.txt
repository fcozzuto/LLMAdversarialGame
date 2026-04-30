def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            candidates.append((dx, dy, nx, ny))

    def man(a, b, c, d):
        ax = a - c
        ay = b - d
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    if not candidates:
        return [0, 0]

    if resources:
        # Prefer taking/approaching the nearest resource, while keeping distance from opponent.
        best = None
        best_val = None
        for dx, dy, nx, ny in candidates:
            dres = 10**9
            for rx, ry in resources:
                dd = man(nx, ny, rx, ry)
                if dd < dres:
                    dres = dd
            dop = man(nx, ny, ox, oy)
            # Tie-break deterministically: prefer smaller dx then dy.
            val = (-dres, dop, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # If no visible resources, move to the center while avoiding opponent proximity.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_val = None
    for dx, dy, nx, ny in candidates:
        # center distance (smaller better) and opponent distance (larger better)
        dc = abs(nx - cx) + abs(ny - cy)
        dop = man(nx, ny, ox, oy)
        val = (-dc, dop, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)
    return [int(best[0]), int(best[1])]