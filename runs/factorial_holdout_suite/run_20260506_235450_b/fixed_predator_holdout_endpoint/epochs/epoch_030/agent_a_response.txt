def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Pick best move by targeting resources where we can swing the contest,
    # and if opponent is ahead to a resource, rush to intercept it earlier.
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # compute current "ahead" resource for opponent from this prospective state
        best_res_val = -10**18
        worst_opp_close = 10**9
        for rx, ry in resources:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            swing = opp_d - our_d  # positive means we are closer than opp
            # if opp is closer, still try to minimize our distance (intercept)
            # and penalize resources where opp is very close already.
            block = -md(nx, ny, rx, ry)
            opp_close = opp_d
            val = swing * 10 - our_d + (0 if our_d <= opp_d else block * 0.1) - opp_close * 0.05
            if val > best_res_val:
                best_res_val = val
            if opp_close < worst_opp_close:
                worst_opp_close = opp_close

        # Additional denial term: if opponent is very close to some resource,
        # move toward the opponent to disrupt their timing.
        opp_to_action = md(nx, ny, ox, oy)
        denom = 1 + min(worst_opp_close, 10)
        denial = 5.0 * (10.0 - denom) - 0.3 * opp_to_action

        total = best_res_val + denial
        if total > best_val:
            best_val = total
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]