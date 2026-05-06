def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    # Evaluate each move by the best resource we can reach "soonest" relative to opponent.
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            nx, ny = x, y  # engine would keep us in place
        # Prefer moves that increase our lead on the most contestable resource.
        mv_best_tv = -10**18
        mv_best_dme = 10**9
        mv_best_dopp = 10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            lead = d_opp - d_me  # positive means we are closer
            # Strongly prioritize positive lead; also penalize being far.
            tv = lead * 1000 - d_me + 0.01 * d_opp
            if tv > mv_best_tv or (tv == mv_best_tv and (d_me < mv_best_dme or (d_me == mv_best_dme and (d_opp < mv_best_dopp or (d_opp == mv_best_dopp and (rx, ry) < (mv_best_tx, mv_best_ty)))))):
                mv_best_tv = tv
                mv_best_dme = d_me
                mv_best_dopp = d_opp
                mv_best_tx, mv_best_ty = rx, ry
        # Add a slight tie-break towards moving in the direction of the chosen resource.
        step_bias = -0.001 * man(nx, ny, mv_best_tx, mv_best_ty)
        total = mv_best_tv + step_bias
        cand = (total, mv_best_dme, mv_best_dopp, dx, dy, nx, ny)
        if best is None or cand > best:
            best = cand

    return [best[3], best[4]]