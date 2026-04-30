def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_pen = 0
    if resources:
        for rx, ry in resources:
            # small preference to reduce risk when opponent is very close to some resource
            d_opp = man((ox, oy), (rx, ry))
            if d_opp <= 1:
                opp_pen -= 1
    else:
        opp_pen = 0

    best = None
    # Score aims to pick a move that leaves us closer than opponent to at least one resource.
    # Score is maximized: larger is better. Deterministic tie-break by lexicographic (dx,dy).
    if resources:
        for dx, dy, nx, ny in moves:
            mypos = (nx, ny)
            best_res_delta = -10**9
            best_my_dist = 10**9
            best_opp_dist = 10**9
            for rx, ry in resources:
                rpos = (rx, ry)
                dm = man(mypos, rpos)
                do = man((ox, oy), rpos)
                delta = do - dm  # positive means we are closer
                if delta > best_res_delta or (delta == best_res_delta and (dm < best_my_dist or (dm == best_my_dist and do < best_opp_dist))):
                    best_res_delta = delta
                    best_my_dist = dm
                    best_opp_dist = do
            # Encourage actually getting there fast and securing advantage; slight penalty if walking into opponent
            score = best_res_delta * 10 - best_my_dist + (best_opp_dist <= best_my_dist) * (-3) + opp_pen
            cand = (score, -best_my_dist, -best_res_delta, dx, dy)
            if best is None or cand > best:
                best = cand
        return [int(best[3]), int(best[4])]
    else:
        # No resources visible: drift toward the center-ish of the map while avoiding being too close to opponent
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in moves:
            dcenter = abs(nx - cx) + abs(ny - cy)
            dthrough = abs(nx - ox) + abs(ny - oy)
            score = -dcenter - (dthrough <= 2) * 5
            cand = (score, dx, dy)
            if best is None or cand > best:
                best = cand
        return [int(best[1]), int(best[2])]