def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obs_set:
                nx, ny = sx, sy
            d = dist2((nx, ny), (tx, ty))
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    us = (sx, sy)
    op = (ox, oy)
    # Pick opponent's best remaining denial target (closest to opponent).
    opp_target = min(resources, key=lambda r: dist2(op, r))
    # Pick our best resource target (closest to us).
    my_target = min(resources, key=lambda r: dist2(us, r))

    # Intercept hint: move toward cell that reduces opponent->target distance while staying near our path.
    def intercept_cell():
        mx = (opp_target[0] + ox) // 2
        my = (opp_target[1] + oy) // 2
        mx = clamp(mx, 0, w - 1)
        my = clamp(my, 0, h - 1)
        if (mx, my) in obs_set:
            # deterministic fallback: step one closer to the target
            sx2, sy2 = ox, oy
            step_dx = 1 if opp_target[0] > sx2 else -1 if opp_target[0] < sx2 else 0
            step_dy = 1 if opp_target[1] > sy2 else -1 if opp_target[1] < sy2 else 0
            mx2 = clamp(sx2 + step_dx, 0, w - 1)
            my2 = clamp(sy2 + step_dy, 0, h - 1)
            return (sx2, sy2) if (mx2, my2) in obs_set else (mx2, my2)
        return (mx, my)

    ic = intercept_cell()

    best = None
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obs_set:
            nx, ny = sx, sy

        # Our progress
        to_my = dist2((nx, ny), my_target)
        # Denial/protection: prefer moves that make opponent->target harder (larger distance increase relative)
        before_opp = dist2(op, opp_target)
        after_opp = dist2(op, opp_target)  # opponent position fixed this turn; use our position to contest
        # Contest pressure via being near the line-of-approach (intercept cell) and near our target simultaneously.
        contest = dist2((nx, ny), ic)
        # Additional resource-denial: being closer to the opponent's target than opponent is (discourage dive)
        my_vs_opp_target = dist2((nx, ny), opp_target) - dist2(op, opp_target)

        val = (to_my, contest, -my_vs_opp_target, after_opp, dx == 0 and dy == 0)
        if best is None or val < best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]