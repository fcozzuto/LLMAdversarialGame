def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0:
            d1 = -d1
        d2 = y1 - y2
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    if resources:
        best = None
        best_gain = -10**9
        best_sd = 10**9
        for rx, ry in resources:
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd
            if gain > best_gain or (gain == best_gain and sd < best_sd):
                best_gain = gain
                best_sd = sd
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_score = 10**18
    opp_best = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            myd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)
            # Lower is better; primary is being closer to target, secondary is reducing opponent lead.
            score = myd - od
            opplead = od - md(nx, ny, tx, ty)
            if score < best_score or (score == best_score and opplead > opp_best):
                best_score = score
                opp_best = opplead
                best_move = [dx, dy]

    return best_move