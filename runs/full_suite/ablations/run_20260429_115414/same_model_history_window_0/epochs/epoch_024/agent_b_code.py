def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def clamp(p):
        x, y = p
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # If no resources known, drift toward center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = clamp((sx + dx, sy + dy))
            if (nx, ny) in obstacles:
                continue
            score = -abs(nx - cx) - abs(ny - cy) + 0.1 * (abs(nx - ox) + abs(ny - oy))
            cand = (score, -(dx != 0 and dy != 0), -abs(dx) - abs(dy), dx, dy)
            if best is None or cand > best:
                best = cand
        return [best[3], best[4]]

    # Evaluate candidate moves by how well they improve access to a resource vs opponent.
    best = None
    for dx, dy in moves:
        nx, ny = clamp((sx + dx, sy + dy))
        if (nx, ny) in obstacles:
            continue

        # Local safety: discourage stepping closer to opponent if it would cost capture.
        opp_close = abs(nx - ox) + abs(ny - oy)
        opp_term = -0.08 * opp_close

        # Main term: pick the resource that is most favorable after the move.
        best_res = None
        for rx, ry in resources:
            d_self = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)

            # Prefer immediate collection; otherwise, prefer resources where we "beat" opponent.
            if d_self == 0:
                res_score = 1e6
            else:
                # Balance: lower d_self is good; higher d_opp is good.
                # Also encourage moving along diagonals to reduce distance efficiently.
                lead = (d_opp - d_self)
                res_score = 500.0 * (lead >= 0) + 20.0 * lead - 1.2 * d_self

            # Slightly penalize moving to a resource that is also within 1 step of opponent.
            if d_opp <= 1 and d_self > 0:
                res_score -= 30.0

            # Choose best resource for this move
            cand = res_score
            if best_res is None or cand > best_res:
                best_res = cand

        score = best_res + opp_term

        # Tie-breakers: prefer moves that reduce distance to chosen target and avoid staying still if not best.
        stay_pen = -0.15 if (dx == 0 and dy == 0) else 0.0
        diag_pref = 0.03 if (dx != 0 and dy != 0) else 0.0
        cand = (score + stay_pen + diag_pref, -abs(dx) - abs(dy), dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[2], best[3]]