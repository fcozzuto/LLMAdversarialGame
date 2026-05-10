def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)
    opp_is_pursuer = ("purs" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursuer" in opp_role)
    pursue = self_is_pursuer or (not opp_is_pursuer)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def wall_pen(x, y):
        d = x
        if y < d: d = y
        t = w - 1 - x
        if t < d: d = t
        t = h - 1 - y
        if t < d: d = t
        return -0.08 * d  # avoid edges/boundaries deterministically

    def mobility(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    best_score = -10**18 if pursue else 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # Encourage approaching (pursuer) or escaping (evader) + avoid mobility traps
        if pursue:
            score = -dist + 0.25 * mobility(nx, ny) + wall_pen(nx, ny)
        else:
            score = dist + 0.25 * mobility(nx, ny) + wall_pen(nx, ny)
        if best is None or (score > best_score if pursue else score < best_score):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]