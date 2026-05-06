def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty)) - man(nx, ny, 0, 0) * 0.01
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Evaluate each possible move by considering how much better we are than opponent for resources,
    # plus a denial term for resources where opponent is currently closer.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        best_gain = -10**18
        deny_best = -10**18
        closest_us = 10**9

        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # If we are closer (or can get there at same time), gain.
            gain = (od - sd) * 10 - sd
            if gain > best_gain:
                best_gain = gain
            # Deny: focus on resources opponent is closer to now.
            opp_ahead = (cheb(x, y, rx, ry) - od)
            if opp_ahead > 0:
                deny = (od - sd) * 12 - sd
                if deny > deny_best:
                    deny_best = deny
            # Small tie-break: move toward closer resource overall.
            d0 = cheb(nx, ny, rx, ry)
            if d0 < closest_us:
                closest_us = d0

        # If opponent is strongly ahead on some resource, increase weight on denial.
        opp_total_ahead = 0
        for rx, ry in resources:
            opp_total_ahead = max(opp_total_ahead, cheb(x, y, rx, ry) - cheb(ox, oy, rx, ry))
        deny_weight = 1.0 + (opp_total_ahead if opp_total_ahead > 0 else 0) * 0.2
        v = best_gain + deny_best * deny_weight - closest_us * 0.4 - man(nx, ny, ox, oy) * 0.02

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]