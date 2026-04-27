def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]) or [0, 0])
    ox, oy = map(int, observation.get("opponent_position", [0, 0]) or [0, 0])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    cands = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cands.append((dx, dy, nx, ny))
    if not cands:
        return [0, 0]

    if resources:
        opp = (ox, oy)
        best = None
        for dx, dy, nx, ny in cands:
            my = (nx, ny)
            d_me_opp = man(my, opp)
            val = -10**9
            for rx, ry in resources:
                r = (rx, ry)
                myd = man(my, r)
                opd = man(opp, r)
                # Prefer resources I'm closer to; avoid going too far and prefer cutting off opponent.
                s = (opd - myd) * 2 - myd + 0.1 * d_me_opp
                if myd == 0:
                    s += 1000
                val = max(val, s)
            cand_score = val
            if best is None or cand_score > best[0]:
                best = (cand_score, dx, dy)
        return [int(best[1]), int(best[2])]

    # No resources visible: move toward center while keeping some distance from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in cands:
        myd = man((nx, ny), (cx, cy))
        dist_opp = man((nx, ny), (ox, oy))
        cand_score = -myd + 0.05 * dist_opp
        if best is None or cand_score > best[0]:
            best = (cand_score, dx, dy)
    return [int(best[1]), int(best[2])]