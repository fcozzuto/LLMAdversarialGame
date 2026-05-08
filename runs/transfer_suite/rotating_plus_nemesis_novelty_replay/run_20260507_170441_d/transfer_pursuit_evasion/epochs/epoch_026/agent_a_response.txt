def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    role = str(observation.get("self_role", "")).lower()
    pursuer = ("purs" in role) or ("tag" in role) or ("hunter" in role) or ("catch" in role)

    best = (0, 0)
    if pursuer:
        best_score = -10**18
        cap_d2 = dist2(ox, oy, ox, oy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = dist2(nx, ny, ox, oy)
            if d == cap_d2:
                return [dx, dy]
            edge_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
            score = -d - 0.05 * edge_pen
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]
    else:
        best_score = -10**18
        # Evader: maximize distance, avoid moving into proximity of obstacles, and bias toward farthest corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = None
        far_d = -1
        for cx, cy in corners:
            d = dist2(cx, cy, ox, oy)
            if d > far_d:
                far_d = d
                far_corner = (cx, cy)
        cx, cy = far_corner
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d_to_p = dist2(nx, ny, ox, oy)
            # obstacle proximity penalty
            prox = 0
            for (bx, by) in obstacles:
                adx = nx - bx
                ady = ny - by
                dd = adx * adx + ady * ady
                if dd <= 4:  # within sqrt(4)
                    prox += (5 - dd)
            corner_bias = dist2(cx, cy, ox, oy) - dist2(cx, cy, nx, ny)
            edge_pen = (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)
            score = d_to_p + 0.03 * corner_bias - 0.2 * prox - 0.02 * edge_pen
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]