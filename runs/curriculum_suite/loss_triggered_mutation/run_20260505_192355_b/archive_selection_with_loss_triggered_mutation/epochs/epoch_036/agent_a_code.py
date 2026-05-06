def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not res:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - cx) + abs(ny - cy)
            key = (d, abs(nx - ox) + abs(ny - oy))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Favor resources where we are closer than the opponent (positive gap).
        # If ties, favor smaller self distance; then reduce opponent access.
        best_gap = None
        best_ds = None
        best_do = None
        for rx, ry in res:
            dS = md(nx, ny, rx, ry)
            dO = md(ox, oy, rx, ry)
            gap = dO - dS
            if best_gap is None or (gap > best_gap) or (gap == best_gap and dS < best_ds) or (gap == best_gap and dS == best_ds and dO < best_do):
                best_gap, best_ds, best_do = gap, dS, dO

        # Additional deterministic tiebreakers: avoid moving into immediate proximity of opponent,
        # and slightly prefer advancing toward the chosen "best" direction via self-opp distance reduction.
        opp_close_penalty = -md(nx, ny, ox, oy)
        key = (-best_gap, best_ds, best_do, opp_close_penalty, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]