def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_step(tx, ty):
        cx, cy = sx, sy
        dxs = 0 if tx == cx else (1 if tx > cx else -1)
        dys = 0 if ty == cy else (1 if ty > cy else -1)
        candidates = []
        # Prefer diagonal when it reduces both coordinates (deterministic ordering)
        for dx, dy in [ (dxs, dys), (dxs, 0), (0, dys), (dxs, -dys), (-dxs, dys), (0, 0) ]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((nx, ny))
        # If diagonal is blocked, pick the move that gets closest to target; tie-break by opponent distance
        best = None
        for nx, ny in candidates:
            ds = man(nx, ny, tx, ty)
            do = man(nx, ny, ox, oy)
            val = (ds, do, nx, ny)
            if best is None or val < best[0]:
                best = (val, nx, ny)
        return 0 if best is None else (best[1] - cx), 0 if best is None else (best[2] - cy)

    if resources:
        # Choose resource maximizing "self lead" over opponent; then by self distance and coordinates.
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # self must arrive first (or least later); prioritize lead over raw distance
            lead = do - ds
            # Slight preference for positions that are also far from opponent next to reduce contention
            opp_pressure = man(rx, ry, ox, oy)
            key = (-lead, ds, opp_pressure, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        _, tx, ty = best[0], best[1], best[2]
        dx, dy = best_step(tx, ty)
        return [int(dx), int(dy)]

    # No visible resources: move toward the most "valuable" corner route (opponent-avoidance).
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    best = None
    for cx, cy in corners:
        if (cx, cy) in obstacles:
            continue
        ds = man(sx, sy, cx, cy)
        do = man(ox, oy, cx, cy)
        key = (ds - do * 0.5, ds, cx, cy)
        if best is None or key < best[0]:
            best = (key, cx, cy)
    if best is None:
        return [0, 0]
    _, tx, ty = best[0], best[1], best[2]
    dx, dy = best_step(tx, ty)
    return [int(dx), int(dy)]