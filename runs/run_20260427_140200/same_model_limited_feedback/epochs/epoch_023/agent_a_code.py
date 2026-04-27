def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    self_x, self_y = self_pos
    opp_x, opp_y = opp_pos

    obs_set = set((p[0], p[1]) for p in obstacles)
    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_target = None
    best_key = None
    if resources:
        for r in resources:
            rx, ry = r
            myd = cheb(self_x, self_y, rx, ry)
            opd = cheb(opp_x, opp_y, rx, ry)
            key = (myd - opd, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)

    if best_target is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best_target

    cand = []
    order = [(0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    for dx, dy in order:
        nx, ny = self_x + dx, self_y + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        dRes = cheb(nx, ny, tx, ty)
        dOpp = cheb(nx, ny, opp_x, opp_y)
        score = -dRes
        score += 0.2 * dOpp
        # Small anti-grab: prefer keeping distance if opponent is very near
        if dOpp <= 1:
            score -= 2.0
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-(t[0]), t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]