def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = (observation.get("self_role", "") or "").lower()

    deltas = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def freedom(x, y):
        c = 0
        for dx, dy in deltas:
            if valid(x + dx, y + dy):
                c += 1
        return c

    evading = ("evad" in role) or ("runner" in role) or ("fugitive" in role)
    corners = ((0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1))

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        f = freedom(nx, ny)
        cbest = 0
        for cx, cy in corners:
            dd = dist2(nx, ny, cx, cy)
            if dd > cbest:
                cbest = dd
        # pursuer: minimize distance; evader: maximize distance
        base = -d if not evading else d
        # avoid dead-ends and optionally prefer/avoid corners deterministically
        corner_term = -cbest if not evading else cbest
        score = base + 0.35 * f + 0.02 * corner_term
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]