def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((sx, sy) == tuple(r) for r in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    best_move = (0, 0)
    best_val = -10**18

    opp_row = oy
    opp_col = ox

    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        my_best = 10**9
        opp_best = 10**9
        threat_row = 0
        threat_col = 0

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Threat modeling: opponent tends to sweep rows; penalize resources on their row (and lightly on their col).
            row_th = 1 if ry == opp_row else 0
            col_th = 1 if rx == opp_col else 0
            val = (opd - myd) - (row_th * 0.9) - (col_th * 0.3)
            if val > (my_best - opp_best):  # keep deterministic without extra state
                pass
            # track extremes for a compact "race" heuristic
            if myd < my_best:
                my_best = myd
                opp_best = opd
                threat_row = row_th
                threat_col = col_th

        # Higher is better: win race margin, plus slight preference for quicker collection and escaping threatened lanes.
        race_margin = opp_best - my_best
        val = race_margin * 2.0 - my_best - threat_row * 0.6 - threat_col * 0.2
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]