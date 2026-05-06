def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inb(x, y) or (x, y) in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_score(nx, ny):
        if not resources:
            # Pivot toward center while staying obstacle-safe
            cx, cy = w // 2, h // 2
            return -(abs(nx - cx) + abs(ny - cy))
        best = None
        for rx, ry in resources:
            sdr = abs(nx - rx) + abs(ny - ry)
            odr = abs(ox - rx) + abs(oy - ry)
            # Prioritize guaranteed-ish grabs: being closer now matters most.
            # Secondary: reduce distance if contested; small preference for approaching.
            gap = odr - sdr
            contested = 0 if sdr < odr else 1
            # Slightly prefer nearer resources to keep momentum.
            val = (gap, -contested, -sdr, -abs(rx - nx) + -abs(ry - ny))
            if best is None or val > best:
                best = val
        return best

    best_move = [0, 0]
    best_val = None
    # Small 2-step lookahead: prefer moves that keep future options good.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        v1 = step_score(nx, ny)
        # If move is illegal by obstacles, engine keeps us; we filtered.
        v2 = None
        # Lookahead only if v1 indicates progress (resources exist); otherwise keep simple.
        if resources:
            best2 = None
            for ddx, ddy in moves:
                mx, my = nx + ddx, ny + ddy
                if blocked(mx, my):
                    continue
                vtmp = step_score(mx, my)
                if best2 is None or vtmp > best2:
                    best2 = vtmp
            v2 = best2
        val = (v1, v2 if v2 is not None else ())
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move