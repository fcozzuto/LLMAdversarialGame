def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    if resources:
        # pick a resource we can reach earlier (maximize margin opp_dist - self_dist)
        best_r = None
        best_m = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            m = od - sd
            key = (m, -sd, -od, rx, ry)
            if best_m is None or key > best_m:
                best_m = key
                best_r = (rx, ry)

        rx, ry = best_r
        sd0 = man(sx, sy, rx, ry)
        od0 = man(ox, oy, rx, ry)
        favorable = (od0 - sd0) > 0

        if favorable:
            # move to reduce our distance, but prefer moves that increase opponent distance
            best = None
            for dx, dy, nx, ny in moves:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                key = (-sd, -od, dx, dy)
                if best is None or key < best[0]:
                    best = (key, dx, dy)
            return [best[1], best[2]]

        # otherwise intercept: head toward the midpoint between opponent and that resource
        tx, ty = (ox + rx) // 2, (oy + ry) // 2
    else:
        # no resources: contest center line
        tx, ty = (sx + ox) // 2, (sy + oy) // 2

    # generic step toward (tx,ty), with tie-break favoring moves that also move away from opponent
    best = None
    for dx, dy, nx, ny in moves:
        d = man(nx, ny, tx, ty)
        opp_gain = man(nx, ny, ox, oy)
        key = (d, -opp_gain, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]