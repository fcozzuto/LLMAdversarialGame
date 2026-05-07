def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist_manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    if not resources:
        tx = gw - 2 if sx < gw // 2 else 1
        ty = gh - 2 if sy < gh // 2 else 1
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -abs(nx - tx) - abs(ny - ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        self_after_best = -10**18
        for rx, ry in resources:
            sd = dist_manh(nx, ny, rx, ry)
            od = dist_manh(ox, oy, rx, ry)
            steal_adv = od - sd  # positive => we're closer
            v = steal_adv * 10 - sd
            if v > self_after_best:
                self_after_best = v
        # prefer moves that keep tempo: small sd if best opportunities tie
        tie_break = 0
        if self_after_best == best_val:
            tie_break = -(abs(nx - sx) + abs(ny - sy))
        if self_after_best > best_val or (self_after_best == best_val and tie_break < 0):
            best_val = self_after_best
            best_move = [dx, dy]

    return best_move