def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_key = None
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obst:
            continue

        best_adv = None
        best_d = None
        best_od = None

        # Priority: maximize (opp_dist - my_dist) to the resource we can contest.
        # Tie-break: closer to that resource; then closer to opponent (to enable denial-counterplay).
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if best_adv is None or adv > best_adv or (adv == best_adv and (myd < best_d or (myd == best_d and opd < best_od))):
                best_adv = adv
                best_d = myd
                best_od = opd

        # Additional: avoid moves that give opponent immediate capture advantage nearby.
        # Use current distances to the closest resource as a mild stabilizer.
        my_to_opp = cheb(nx, ny, ox, oy)
        opp_best_now = None
        my_best_now = None
        for rx, ry in resources:
            myd_now = cheb(sx, sy, rx, ry)
            opd_now = cheb(ox, oy, rx, ry)
            if my_best_now is None or myd_now < my_best_now:
                my_best_now = myd_now
            if opp_best_now is None or opd_now < opp_best_now:
                opp_best_now = opd_now
        opp_pressure = 0
        if opp_best_now is not None and my_best_now is not None:
            opp_pressure = (opp_best_now - my_best_now)

        key = (best_adv, -best_od if best_od is not None else 0, -my_to_opp, -opp_pressure, -best_d)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move