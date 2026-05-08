def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = (observation.get("self_role") or "").lower()
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def manh(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def cheb(x1, y1, x2, y2): return max(abs(x1 - x2), abs(y1 - y2))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    is_pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuer" in role)
    # For evasion, infer where the pursuer likely is: use current opponent position only (no velocity in observation).
    target_cx, target_cy = 0, 0
    if is_pursuer:
        # Chase: minimize distance; slight preference to moves that reduce chebyshev.
        best = None  # (score, dx, dy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d1 = manh(nx, ny, ox, oy)
            d2 = cheb(nx, ny, ox, oy)
            # Penalize stepping into a square where you have fewer options (helps avoid getting blocked).
            options = 0
            for adx, ady in dirs:
                ax, ay = nx + adx, ny + ady
                if free(ax, ay):
                    options += 1
            # score: lower is better
            score = (d1, d2, -options)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]
    else:
        # Evade: maximize distance from opponent while steering toward the farthest corner.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # Choose the corner that is farthest from the opponent, then move to reduce distance to that corner.
        far_corner = max(corners, key=lambda c: manh(c[0], c[1], ox, oy))
        target_cx, target_cy = far_corner[0], far_corner[1]

        best = None  # (score, dx, dy)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            dist_from_p = manh(nx, ny, ox, oy)
            dist_to_corner = manh(nx, ny, target_cx, target_cy)
            options = 0
            for adx, ady in dirs:
                ax, ay = nx + adx, ny + ady
                if free(ax, ay):
                    options += 1
            # score: higher is better => use negative for ordering as tuple
            score = (-dist_from_p, dist_to_corner, -options)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]] if best is not None else [0, 0]