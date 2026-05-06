def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    midx = (sx + ox) / 2.0
    midy = (sy + oy) / 2.0

    def score_cell(nx, ny):
        best_our_d = 10**9
        best_opp_d = 10**9
        best_gap = -10**9
        best_res = None
        for rx, ry in resources:
            d_our = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            if d_our < best_our_d:
                best_our_d = d_our
            if d_opp < best_opp_d:
                best_opp_d = d_opp
            gap = d_opp - d_our
            if gap > best_gap:
                best_gap = gap
                best_res = (rx, ry)

        # Prefer resources where we are ahead (positive gap), otherwise try to become ahead.
        ahead_bonus = max(0, best_gap) * 100

        # Interceptor component: when opponent is very close to their nearest resource, we push toward their nearest.
        intercept_target = None
        opp_near_d = 10**9
        for rx, ry in resources:
            d_opp = dist(ox, oy, rx, ry)
            if d_opp < opp_near_d:
                opp_near_d = d_opp
                intercept_target = (rx, ry)
        intercept = 0 if intercept_target is None else (0 if opp_near_d > 6 else (6 - opp_near_d) * 12 - dist(nx, ny, intercept_target[0], intercept_target[1]))

        # Midline pressure: prefer moves that move us "through" the midline toward opponent's side.
        mid_push = -((nx - midx) ** 2 + (ny - midy) ** 2)

        # Small obstacle-safe tie-break: prefer closer to our best resource.
        tail = -best_our_d

        # If we're likely behind (best_gap <= 0), penalize a bit to avoid repeating losing paths.
        behind_pen = 0 if best_gap > 0 else (-best_gap) * 10
        return ahead_bonus + intercept + mid_push + tail - behind_pen

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sc = score_cell(nx, ny)
        if best is None or sc > best or (sc == best and (dx, dy) < best_move):
            best = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]