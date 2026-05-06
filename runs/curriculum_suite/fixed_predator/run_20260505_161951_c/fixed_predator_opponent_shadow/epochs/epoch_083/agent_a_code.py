def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        bestv = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = man(nx, ny, tx, ty)
            oppd = man(nx, ny, ox, oy)
            key = (d, -oppd, dx, dy)
            if bestv is None or key < bestv:
                bestv, best = key, (dx, dy)
        return [best[0], best[1]]

    best_cell = None
    best_key = None
    # deterministic tie-breaking: (key, dx, dy)
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # find nearest resource for self and how contested it is
        self_best = 10**9
        opp_best = 10**9
        contest = 0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            if sd < self_best: self_best = sd
            if od < opp_best: opp_best = od
        # primary: get to a resource fast; secondary: prevent opponent from having advantage
        # contest measures if we move into a region where opponent is closer to top resources
        contested_gain = 0
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # if opponent is already much closer, we try to deny by moving closer than them
            if od <= sd:
                contested_gain += (od - sd) * 2 + 1
            else:
                contested_gain -= (sd - od)
        # small preference to reduce distance to opponent when we can't secure a resource quickly (intercept)
        opp_int = man(nx, ny, ox, oy)
        key = (
            self_best,
            contested_gain,
            opp_int if self_best > 1 else 0,
            # discourage wandering: prefer moving generally towards the best self resource
            abs(nx - sx) + abs(ny - sy),
            dx,
            dy,
        )
        if best_key is None or key < best_key:
            best_key = key
            best_cell = (dx, dy)

    return [best_cell[0], best_cell[1]]