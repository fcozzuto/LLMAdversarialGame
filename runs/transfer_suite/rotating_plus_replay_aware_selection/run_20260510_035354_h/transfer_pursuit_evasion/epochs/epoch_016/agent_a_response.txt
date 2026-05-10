def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

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

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    def corner_targets():
        return [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_d = d2(nx, ny, ox, oy)

        # Obstacle-aware nudge: avoid moving next to obstacles too often (helps evasion and safe pursuit).
        near_obs = 0
        for (px, py) in obstacles:
            if abs(nx - px) <= 1 and abs(ny - py) <= 1:
                near_obs += 1

        # Deterministic corner bias to break ties and encourage decisive motion.
        # Pursuer: bias toward corners that are farther from opponent's current corner-choice,
        # Evader: bias toward the farthest corner from opponent.
        c_bias = 0
        if obstacles is not None:
            corners = corner_targets()
            best_corner_dist = -1
            worst_corner_dist = 10**18
            for cx, cy in corners:
                cd_self = d2(nx, ny, cx, cy)
                cd_opp = d2(ox, oy, cx, cy)
                if cd_self > best_corner_dist:
                    best_corner_dist = cd_self
                if cd_opp < worst_corner_dist:
                    worst_corner_dist = cd_opp
            if i_am_pursuer:
                c_bias = -best_corner_dist + 0.5 * worst_corner_dist
            else:
                c_bias = best_corner_dist - 0.5 * worst_corner_dist

        if i_am_pursuer:
            # Higher is better: prefer smaller opp distance, penalize near obstacles, small c_bias.
            score = -opp_d - 0.3 * near_obs + 0.01 * c_bias
        else:
            # Higher is better: prefer larger opp distance, penalize near obstacles.
            score = opp_d - 0.3 * near_obs + 0.01 * c_bias

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]