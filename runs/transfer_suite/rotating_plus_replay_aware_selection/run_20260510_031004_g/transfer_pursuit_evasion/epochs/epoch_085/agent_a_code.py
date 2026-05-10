def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def nearest_corner_dist(x, y):
        dmin = 10**9
        for cx, cy in corners:
            d = (cx - x) * (cx - x) + (cy - y) * (cy - y)
            if d < dmin:
                dmin = d
        return dmin

    def mobility(x, y):
        m = 0
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                m += 1
        return m

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18 if self_is_pursuer else 10**18

    # Pursuer: reduce distance; also drift toward opponent's likely corner line.
    # Evader: maximize distance; also keep mobility high while steering away from pursuer.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        my_mob = mobility(nx, ny)

        if self_is_pursuer:
            opp_corner_dist = nearest_corner_dist(ox, oy)
            # Encourage moves that reduce distance while also making the "opponent corner target"
            # less reachable from our perspective (greedy interception).
            corner_seek = nearest_corner_dist(nx, ny)
            score = (-dist2) + 0.06 * my_mob - 0.01 * corner_seek + 0.001 * (opp_corner_dist - corner_seek)
            if score > best_score:
                best_score = score
                best = (dx, dy)
        else:
            # Evader aims away from pursuer, avoid low mobility, and steer away from pursuer's access.
            pursuer_corner_dist = nearest_corner_dist(ox, oy)
            my_corner_dist = nearest_corner_dist(nx, ny)
            score = (dist2) + 0.06 * my_mob + 0.01 * pursuer_corner_dist - 0.01 * my_corner_dist
            if score < best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]