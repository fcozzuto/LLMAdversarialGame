def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    adj8 = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obst_pen(x, y):
        if (x, y) in occ:
            return 10**9
        p = 0
        for dx, dy in adj4:
            if (x + dx, y + dy) in occ:
                p += 12
        for dx, dy in adj8:
            if (x + dx, y + dy) in occ:
                p += 2
        return p

    if not resources:
        # return to center-ish while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            v = man(nx, ny, cx, cy) + obst_pen(nx, ny)
            if v < bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # pick a "contested" resource we are relatively closer to
    best_r = None
    best_rel = 10**18
    for r in resources:
        rx, ry = r[0], r[1]
        ar = man(sx, sy, rx, ry)
        br = man(ox, oy, rx, ry)
        # prefer resources where our advantage is higher; if tie, closer to us
        rel = (ar - br) * 1000 + ar
        if rel < best_rel:
            best_rel = rel
            best_r = (rx, ry)

    rx, ry = best_r
    # evaluate one-step moves toward the chosen resource, with obstacle and "interference" bias
    # Interference: also consider moving to reduce distance to opponent (denser fights can block).
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue
        v = man(nx, ny, rx, ry) * 3
        v += obst_pen(nx, ny)
        v += man(nx, ny, ox, oy) * 0.2  # keep some spacing; lower is closer
        if v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]