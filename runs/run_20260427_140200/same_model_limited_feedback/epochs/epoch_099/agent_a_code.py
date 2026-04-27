def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def clamp(x, a, b):
        return a if x < a else b if x > b else x

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for diagonal grid

    opp = (ox, oy)
    target = None
    if resources:
        # baseline target: nearest resource from our current position
        target = min(resources, key=lambda r: dist((sx, sy), r))

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            sc = -10**9
        else:
            if (nx, ny) in obs:
                sc = -10**8
            else:
                my = (nx, ny)
                if resources:
                    # Race: how much closer we are than opponent to the best resource
                    best_race = -10**9
                    best_md = 10**9
                    for r in resources:
                        d_m = dist(my, r)
                        d_o = dist(opp, r)
                        if d_m < best_md:
                            best_md = d_m
                        dr = d_o - d_m
                        if dr > best_race:
                            best_race = dr
                    # Obstacle proximity (discourage stepping near obstacles)
                    adj_obs = 0
                    for ex in (-1, 0, 1):
                        for ey in (-1, 0, 1):
                            if (nx + ex, ny + ey) in obs:
                                adj_obs += 1
                    corner_bias = 0.0
                    # Prefer moving toward a corner away from opponent when race is poor
                    if best_race < 0:
                        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
                        corner_bias = 0.05 * max(dist(my, c) for c in corners) - 0.05 * dist(my, opp)
                    sc = 2.0 * best_race - 0.08 * best_md - 0.25 * adj_obs + corner_bias
                else:
                    sc = dist(my, opp) + 0.01 * (nx + ny)  # just separate
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]