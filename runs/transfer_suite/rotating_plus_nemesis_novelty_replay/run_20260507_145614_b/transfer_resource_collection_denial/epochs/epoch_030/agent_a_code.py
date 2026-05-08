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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    # Opponent bias: estimate where opponent will pressure next by nearest resource.
    # This helps avoid "races" we are losing while still pursuing winable captures.
    opp_best = None
    opp_best_d = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best_d:
            opp_best_d = d
            opp_best = (rx, ry)

    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in deltas:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        # Local score: choose the most favorable resource race outcome from (nx,ny).
        # Utility: positive when we can arrive earlier than opponent.
        local = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If sd==od, we still prefer it but with smaller weight (race likely).
            util = (od - sd) * 1000 - sd * 5
            if od == sd:
                util -= 20
            # Small diversification: prefer resources that are not too close to opponent's nearest.
            if opp_best is not None:
                util -= cheb(opp_best[0], opp_best[1], rx, ry)
            if util > local:
                local = util

        # Secondary: avoid stepping into cells that increase opponent advantage too much globally.
        # (Encourages lines that cut opponent access.)
        opp_step_adv = (cheb(nx, ny, opp_best[0], opp_best[1]) if opp_best is not None else 0) if opp_best is not None else 0
        val = local - opp_step_adv
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]