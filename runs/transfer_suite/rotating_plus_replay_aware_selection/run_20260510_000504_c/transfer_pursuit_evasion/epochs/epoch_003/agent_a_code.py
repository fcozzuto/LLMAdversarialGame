def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role", "") or "").lower()

    # Deterministic move order (diagonals last to reduce zigzag risk)
    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def freedom(x, y):
        c = 0
        for ddx, ddy in deltas:
            tx, ty = x + ddx, y + ddy
            if valid(tx, ty):
                c += 1
        return c

    def far_corner_score(x, y):
        # Bias evader to farthest corner from pursuer (deterministic)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = -1
        for cx, cy in corners:
            d = (cx - x) * (cx - x) + (cy - y) * (cy - y)
            if d > best:
                best = d
        return best

    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role)
    best_move = [0, 0]
    best_score = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d2 = dist2(nx, ny)

        # Small obstacle pressure (prefer positions with more legal options)
        f = freedom(nx, ny)

        # Evader tends to stay away and drift to a far corner, while avoiding immediate regress toward pursuer
        if pursuer:
            # Minimize distance; slight preference for higher freedom (avoid trapping yourself)
            score = (-d2, f, -(abs(nx - ox) + abs(ny - oy)), 0 if (dx == 0 and dy == 0) else 1)
        else:
            # Maximize distance; favor far-corner drift; keep freedom high; discourage staying still if it reduces distance
            corner = far_corner_score(nx, ny)
            score = (d2, f, corner, 1 if not (dx == 0 and dy == 0) else 0)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]