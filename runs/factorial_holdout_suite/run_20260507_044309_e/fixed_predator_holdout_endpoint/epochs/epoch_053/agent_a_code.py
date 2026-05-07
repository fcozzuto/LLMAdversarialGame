def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    if not resources:
        return [0, 0]

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) and (rx, ry) not in blocked:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    target_set = set(res)
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue

        self_at_res = 1 if (nx, ny) in target_set else 0
        self_best = 10**9
        opp_best = 10**9
        opp_after = 10**9

        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            if d_self < self_best: self_best = d_self
            d_opp = md(ox, oy, rx, ry)
            if d_opp < opp_best: opp_best = d_opp
            # extra pressure: resources we could beat immediately
            d_oppt = md(ox, oy, rx, ry)
            if d_oppt < opp_after: opp_after = d_oppt

        # Primary: win the race to some resource (smaller self_best than opp_best)
        val = 0
        val += 10000 * self_at_res
        val += 2000 * (opp_best - self_best)
        # Secondary: go toward resources sooner; discourage moving away
        cur_self_best = 10**9
        for rx, ry in res:
            d0 = md(sx, sy, rx, ry)
            if d0 < cur_self_best: cur_self_best = d0
        val += 50 * (cur_self_best - self_best)
        # Tertiary: stay closer to opponent so they can't safely deny nearby clusters
        val += 0.5 * (md(nx, ny, ox, oy) * -1)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move