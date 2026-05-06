def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res_set = set(tuple(p) for p in resources)

    if not resources:
        # Go toward opponent to contest lanes while staying safe
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_op = man(nx, ny, ox, oy)
            v = -d_op - 0.05 * man(nx, ny, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (nx, ny) < best):
                bestv = v
                best = (nx, ny)
        if best is None:
            return [0, 0]
        return [best[0] - sx, best[1] - sy]

    # Compete for the best resource considering opponent progress
    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) in res_set:
            v = 10**6  # immediate collection
        else:
            my_c = man(nx, ny, cx, cy)
            opp_d = man(nx, ny, ox, oy)
            v = -0.08 * my_c - 0.03 * opp_d
            best_res = None
            for rx, ry in resources:
                d_me = man(nx, ny, rx, ry)
                d_op = man(ox, oy, rx, ry)
                # Favor states where we are closer than opponent by margin,
                # but avoid very long detours.
                cand = (d_op - d_me) - 0.18 * d_me
                if best_res is None or cand > best_res:
                    best_res = cand
            v += best_res if best_res is not None else 0
        if bestv is None or v > bestv or (v == bestv and (nx, ny) < best):
            bestv = v
            best = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[0] - sx, best[1] - sy]