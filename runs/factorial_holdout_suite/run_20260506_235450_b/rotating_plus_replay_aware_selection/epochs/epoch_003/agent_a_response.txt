def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    occ = (sx, sy)
    if occ in obstacles:
        for mv in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]:
            nx, ny = sx + mv[0], sy + mv[1]
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [mv[0], mv[1]]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    prefs = []
    us_closer = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        dsu = man((sx, sy), (rx, ry))
        dpo = man((ox, oy), (rx, ry))
        if dsu <= dpo:
            us_closer.append((rx, ry, dsu, dpo))
    pool = us_closer if us_closer else [(rx, ry, man((sx, sy), (rx, ry)), man((ox, oy), (rx, ry))) for rx, ry in resources if (rx, ry) not in obstacles]
    if not pool:
        return [0, 0]

    # Score a move by reaching a "safer" resource (not currently closest to opponent), with slight blocking bias.
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best = None
        for rx, ry, dsu, dpo in pool[:min(8, len(pool))]:
            cur_us = man((nx, ny), (rx, ry))
            # If opponent is much closer, avoid unless we can still beat them quickly.
            if dpo + 1 < cur_us:
                continue
            key = (cur_us, dpo, abs(rx - ox) + abs(ry - oy))
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        if best is None:
            # If all avoided, just get closest reachable resource.
            rx, ry, _, _ = pool[0]
            val = (man((nx, ny), (rx, ry)), man((nx, ny), (ox, oy)))
        else:
            (k1, k2, k3), (rx, ry) = best
            # Blocking: prefer moves that increase opponent's distance to the same target.
            val = (k1, -k2, -k3, man((nx, ny), (rx, ry)) - man((ox, oy), (rx, ry)))
        prefs.append((val, (mx, my)))

    if not prefs:
        return [0, 0]
    prefs.sort()
    return [prefs[0][1][0], prefs[0][1][1]]