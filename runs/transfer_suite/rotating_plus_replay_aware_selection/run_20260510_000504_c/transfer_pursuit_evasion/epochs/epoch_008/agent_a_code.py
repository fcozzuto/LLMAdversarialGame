def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (observation.get("self_role", "") or "").lower()
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuer" in role)
    best_move = [0, 0]
    best_score = None

    def freedom(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        f = freedom(nx, ny)

        # Greedy pursuit: reduce distance; Greedy evasion: increase distance.
        if pursuer:
            score = -d_opp + 0.15 * f
        else:
            # Bias toward staying away from opponent and not losing mobility.
            far_corner = max(dist2(nx, ny, cx, cy) for cx, cy in corners)
            score = d_opp + 0.30 * f + 0.02 * far_corner

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move