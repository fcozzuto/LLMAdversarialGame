def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_key = None
    best_move = [0, 0]

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        # Evaluate this move by the best contest we can win now (largest lead), and then cleanup
        # Lead positive => we arrive earlier (or same) for that contested resource.
        best_lead = None
        best_self_d = None
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            lead = od - sd
            # Prefer winning earlier, then shorter self distance
            if best_lead is None or lead > best_lead or (lead == best_lead and sd < best_self_d):
                best_lead = lead
                best_self_d = sd

        # If no reachable resources, just minimize self distance to any valid resource
        if best_lead is None:
            min_sd = None
            for rx, ry in resources:
                if not cell_ok(rx, ry):
                    continue
                sd = dist(nx, ny, rx, ry)
                if min_sd is None or sd < min_sd:
                    min_sd = sd
            lead = -10**9 if min_sd is None else -min_sd

        # Convert to comparable key:
        # 1) maximize lead (we want od - sd as large as possible)
        # 2) then minimize self distance to that resource
        # 3) then tie-break by avoiding moving into being closer to obstacles (light heuristic)
        # 4) deterministic ordering already from moves list but still add a stable key.
        key = (best_lead if best_lead is not None else -10**9, -(best_self_d if best_self_d is not None else 10**9), nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [nx - sx, ny - sy]

    return best_move