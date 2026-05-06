def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) + abs(dy)

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    self_d0 = man(x, y, ox, oy)

    if not resources:
        best_move = [0, 0]
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            opp_d = man(nx, ny, ox, oy)
            v = (opp_d - self_d0) * 3
            if opp_d <= 2:
                v += (opp_d) * 2
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
        return best_move

    # Choose a target resource that balances being closer than opponent and generally safer.
    best_target = None
    best_tval = -10**18
    for rx, ry in resources:
        sd = man(x, y, rx, ry)
        od = man(ox, oy, rx, ry)
        # Higher if we are closer, lower if opponent is closer
        tval = (od - sd) * 3 + (self_d0 - man(x, y, ox, oy)) * 0 + (sd == 0) * 50
        # Prefer resources that are not too "through the opponent"
        tval -= (man(x, y, ox, oy) <= 2) * 2
        if tval > best_tval or (tval == best_tval and (rx, ry) < best_target):
            best_tval = tval
            best_target = (rx, ry)

    tx, ty = best_target
    on_resource = (x, y) == (tx, ty)
    escape = self_d0 <= 2
    tighten = self_d0 >= 5

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_d = man(nx, ny, ox, oy)
        sd = man(nx, ny, tx, ty)
        res_gain = 35 if (nx, ny) in resources else 0

        # Resource progress (prefer reducing distance), with a safety term.
        progress = (man(x, y, tx, ty) - sd) * 4
        safety = 0
        if escape:
            safety = (opp_d - self_d0) * 6 + (opp_d <= 1) * -20
        elif tighten:
            safety = (opp_d) * 0.5  # don't wander too far

        # Avoid letting opponent get strictly closer while we're not making strong progress.
        opp_delta = man(nx, ny, ox, oy) - self_d0
        penalty = 0
        if opp_d < self_d0 and progress <= 1:
            penalty = (self_d0 - opp_d) * 2

        # Slightly discourage staying if we are not on target.
        stay_pen = 3 if (dx == 0 and dy == 0 and not on_resource) else 0

        v = res_gain + progress + safety - penalty - stay_pen
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move