def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = {(int(x), int(y)) for x, y in obstacles}

    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in sr) and not ("evad" in orr)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def adj_free_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    near_corner = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    target = far_corner if self_is_evader else near_corner

    # Deterministic order: prefer increasing dx then dy
    ordered = sorted(deltas, key=lambda d: (d[0], d[1]))
    best = None
    best_move = [0, 0]

    for dx, dy in ordered:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        d_to_opp = abs(nx - ox) + abs(ny - oy)
        d_to_tgt = abs(nx - target[0]) + abs(ny - target[1])
        safety = adj_free_count(nx, ny)

        # Score: evader maximizes, pursuer minimizes (via common scoring sign flip)
        if self_is_evader:
            score = (d_to_opp * 5.0) + (safety * 1.2) - (d_to_tgt * 0.4)
        else:
            score = (-d_to_opp * 5.0) + (safety * 0.4) - (d_to_tgt * 0.15)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move