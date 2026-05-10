def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    def role_is_purs(role):
        r = (role or "").lower()
        if "purs" in r:
            return True
        if "evad" in r:
            return False
        return None

    sr = role_is_purs(observation.get("self_role"))
    orr = role_is_purs(observation.get("opponent_role"))
    if sr is None:
        sr = (orr is False)
    i_am_pursuer = bool(sr)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def near_obstacle_cost(x, y):
        # Penalize being adjacent to obstacles to avoid getting "stuck"
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in obs:
                    c += 1
        return c

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        dist = d2(nx, ny, ox, oy)
        # If pursuer: minimize distance; if evader: maximize distance.
        sign = -1 if i_am_pursuer else 1

        # Extra heuristic: push toward corners when evading, toward center lanes when pursuing.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner_metric = min(d2(nx, ny, cx, cy) for cx, cy in corners)
        corner_metric_opp = min(d2(ox, oy, cx, cy) for cx, cy in corners)

        score = sign * dist
        score += (-0.15 if i_am_pursuer else 0.15) * (corner_metric - corner_metric_opp)
        score += (-0.6 if i_am_pursuer else -0.3) * near_obstacle_cost(nx, ny)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]