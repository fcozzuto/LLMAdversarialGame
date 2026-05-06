def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy) * 5 - man(nx, ny, cx, cy)
            if best is None or v > bestv or (v == bestv and (nx, ny) < best):
                best, bestv = (nx, ny), v
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    # Pick resource with best tempo advantage (self closer than opponent).
    best_res = None
    bestv = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer cells we can likely secure: (do - ds) and also smaller ds.
        v = (do - ds) * 10 - ds
        if best_res is None or v > bestv or (v == bestv and (rx, ry) < best_res):
            best_res, bestv = (rx, ry), v

    rx, ry = best_res
    cur_d = man(sx, sy, rx, ry)

    # Move to reduce distance to chosen resource; avoid making us easier to intercept.
    # Deterministic tie-break by (nx, ny).
    best_step = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d1 = man(nx, ny, rx, ry)
        # Estimate opponent pressure: how close opponent is to the chosen resource.
        do = man(ox, oy, rx, ry)
        # Slightly prefer moves that also increase distance from opponent when not worsening ds.
        opp_sep = man(nx, ny, ox, oy)
        score = (cur_d - d1) * 100 - d1 - do * 2 + opp_sep * 0.3
        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (sx + best_step[0], sy + best_step[1])):
            best_score = score
            best_step = (dx, dy)

    return [best_step[0], best_step[1]]