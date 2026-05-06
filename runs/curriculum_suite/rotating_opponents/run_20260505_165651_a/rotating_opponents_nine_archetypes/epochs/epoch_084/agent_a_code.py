def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def aligned_bonus(nsx, nsy):
        if nsx == ox or nsy == oy:
            return 0.7
        if (nsx + nsy) == (ox + oy) or (nsx - nsy) == (ox - oy):
            return 0.35
        return 0.0

    # New strategy: choose a "safe steal" resource that opponent is relatively far from,
    # then pick the single best immediate step toward that target, with a small defensive alignment bonus.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nsx, nsy = sx + dx, sy + dy
        if blocked(nsx, nsy):
            continue
        self_to_best = 10**9
        steal_val = -10**18
        for tx, ty in res:
            sd = man(nsx, nsy, tx, ty)
            od = man(ox, oy, tx, ty)
            # prioritize stealing resources where we gain distance advantage (od - sd),
            # with deterministic tie-breaking favoring closer (after) and then lower x,y.
            val = (od - sd) * 10 + (-sd) * 1 + (0.001 * (-(tx * 10 + ty)))
            if val > steal_val:
                steal_val = val
                self_to_best = sd
        opp_gain_block = -man(nsx, nsy, ox, oy) * 0.02  # slightly keep away from aggressive sweeps
        total = steal_val + opp_gain_block + aligned_bonus(nsx, nsy) - (self_to_best * 0.01)
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]