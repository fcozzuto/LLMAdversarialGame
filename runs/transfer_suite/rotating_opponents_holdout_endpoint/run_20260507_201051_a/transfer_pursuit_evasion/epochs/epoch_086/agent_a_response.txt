def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("hunter" in role) or ("seeker" in role) or ("pursuer" in role)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def obstacle_pressure(x, y):
        c = 0
        for dx, dy in neigh8:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    # Cornering bias for pursuer: prefer moves that reduce opponent's access to far corners.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    def corner_spread(x, y):
        # smaller is "more cornered" (closer to fewer corners)
        ds = sorted(dist2(x, y, cx, cy) for cx, cy in corners)
        return ds[0] + 0.25 * ds[1]

    best_move = [0, 0]
    best_val = None

    for dx, dy in neigh8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_own = dist2(nx, ny, ox, oy)
        pres = obstacle_pressure(nx, ny)

        if is_pursuer:
            # minimize distance, avoid obstacle pressure, and slightly corner opponent
            val = 10 * d_own + 3 * pres + 0.8 * corner_spread(ox, oy)
            better = (best_val is None) or (val < best_val)
        else:
            # maximize distance and avoid being boxed in
            val = 10 * (-d_own) + 3 * pres + 0.6 * corner_spread(ox, oy)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]