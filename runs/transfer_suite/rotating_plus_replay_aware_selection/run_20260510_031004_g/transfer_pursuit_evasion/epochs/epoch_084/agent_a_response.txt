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
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                m += 1
        return m

    best = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        mob = mobility(nx, ny)
        corner_bias = abs(nx - far_corner[0]) + abs(ny - far_corner[1])
        # Additional wall pressure: keep away from being corner-trapped when evading
        wall_pen = (0 if inb(nx, ny) else 1) + (1 if nx == 0 or nx == w - 1 else 0) + (1 if ny == 0 or ny == h - 1 else 0)

        if is_pursuer:
            score = (-dist) + (0.35 * mob) + (0.10 * (-corner_bias)) - (0.25 * wall_pen)
        else:
            score = (dist) + (0.25 * mob) + (0.18 * corner_bias) - (0.30 * wall_pen)

        if best_score is None or (score > best_score):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]