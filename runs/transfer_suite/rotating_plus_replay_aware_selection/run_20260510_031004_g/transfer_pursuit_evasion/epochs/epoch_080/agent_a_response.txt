def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or (("evad" in opp_role) and ("evad" not in self_role))

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ddx, ddy = nx - ox, ny - oy
        d2 = ddx * ddx + ddy * ddy

        if is_pursuer:
            # Chase: minimize distance, avoid getting blocked, prefer moves with better local mobility
            mob = 0
            for adx, ady in dirs:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    mob += 1
            # Obstacle penalty if next to obstacle
            adj_obs = 0
            for adx, ady in dirs:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) in obstacles:
                    adj_obs += 1
            score = (-d2) + (0.15 * mob) - (0.1 * adj_obs)
        else:
            # Evade: maximize distance, also avoid trapping near obstacles; bias toward farthest corners
            mob = 0
            for adx, ady in dirs:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    mob += 1
            adj_obs = 0
            for adx, ady in dirs:
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty) and (tx, ty) in obstacles:
                    adj_obs += 1
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            corner_dist = 0
            for cx, cy in corners:
                cd = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                if cd > corner_dist:
                    corner_dist = cd
            score = (d2) + (0.12 * mob) - (0.2 * adj_obs) + (0.01 * corner_dist)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    return [int(best[0]), int(best[1])]