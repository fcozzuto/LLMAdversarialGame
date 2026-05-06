def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # If no resources visible, drift away from opponent toward our corner (robust, deterministic).
    if not resources:
        tx, ty = 0, 0
        if sx > tx: dx = -1
        elif sx < tx: dx = 1
        else: dx = 0
        if sy > ty: dy = -1
        elif sy < ty: dy = 1
        else: dy = 0
        return [dx, dy]

    cx = (w - 1) / 2.0; cy = (h - 1) / 2.0
    center_bias = 0.01

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose the move that maximizes our "can-get-first" margin over any resource.
        best_margin = -10**9
        best_dist_to_resource = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds  # positive => we arrive earlier or equal
            if margin > best_margin or (margin == best_margin and ds < best_dist_to_resource):
                best_margin = margin
                best_dist_to_resource = ds

        # Also slightly prefer moves that reduce our distance to the chosen best resource,
        # and avoid letting the opponent get too good an option.
        opp_best = -10**9
        for rx, ry in resources:
            do = man(nx, ny, rx, ry)  # misuse as "our next position" distance, keeps deterministic cheap coupling
            oo = man(ox, oy, rx, ry)
            opp_margin = man(sx, sy, rx, ry) - oo  # how bad we are relative to opponent, proxy
            if opp_margin > opp_best:
                opp_best = opp_margin

        score = best_margin + (best_dist_to_resource * -0.02) + center_bias * (-(abs(nx - cx) + abs(ny - cy))) + 0.0 * opp_best
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]