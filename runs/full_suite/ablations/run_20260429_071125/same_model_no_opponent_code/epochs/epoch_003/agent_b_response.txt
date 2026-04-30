def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obs)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_ok(x, y):
        return inb(x, y) and (x, y) not in obst

    # Choose a resource target: faster for us, slower for opponent, with slight bias away from opponent corner
    if resources:
        best_r = resources[0]
        best_val = None
        for rx, ry in resources:
            ds = dist(sx, sy, rx, ry)
            do = dist(ox, oy, rx, ry)
            corner_bias = 0.03 * dist(w - 1 - ox, h - 1 - oy, rx, ry)
            # alpha > 1: strongly deny resources the opponent can reach easily
            val = ds - 1.45 * do + corner_bias
            if best_val is None or val < best_val:
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    # If opponent is very close to some resource, prefer moves that increase our chance to intercept nearby
    intercept = None
    best_inter = None
    if resources:
        for rx, ry in resources:
            do = dist(ox, oy, rx, ry)
            if intercept is None or do < best_inter:
                best_inter = do
                intercept = (rx, ry)
        ix, iy = intercept
    else:
        ix, iy = tx, ty

    # Evaluate moves with simple local heuristic
    best_move = [0, 0]
    best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue

            d_me = dist(nx, ny, tx, ty)
            d_opp = dist(nx, ny, ox, oy)

            # Discourage moving into obstacle-adjacent cells; also avoid moving closer to opponent when contesting
            near_obs = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    px, py = nx + ax, ny + ay
                    if (px, py) in obst:
                        near_obs += 1

            d_inter = dist(nx, ny, ix, iy)
            # When opponent is close, prioritize reducing our distance to their likely resource
            opp_close = max(0, 6 - dist(ox, oy, ix, iy))
            contest = -0.55 * opp_close * (d_inter)

            score = (-3.0 * d_me) + (0.20 * d_opp) - (1.4 * near_obs) + contest
            if score > best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move if isinstance(best_move, list) else [0, 0]