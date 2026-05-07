def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if (sx, sy) in obstacles:
        return [0, 0]
    if any((sx, sy) == (rx, ry) for rx, ry in resources):
        return [0, 0]
    if not resources:
        # deterministic fallback: move toward nearest corner away from opponent
        tx, ty = (0, 7) if (sx + (7 - sy)) >= (7 - sx + sy) else (7, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    def obst_adj_pen(nx, ny):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    p += 1
        return p

    best = (-10**18, 10**9, 10**9, 0, 0)  # (adv, time, -opp_time, pen, dx, dy) packed
    best_dxdy = [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # iterate deterministically; prefer earlier resources for tie-break
    resources_sorted = sorted(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))

    for dx, dy, nx, ny in moves:
        # find best target resource for this next cell via race advantage
        cand = (-10**18, 10**9, 10**9)
        for rx, ry in resources_sorted:
            self_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            # want larger opp_d - self_d (we are closer). tie: smaller self_d.
            adv = opp_d - self_d
            # encourage winning the race; if distances equal, go for sooner pickup.
            # also slightly prefer targets that opponent is less likely to reach soon.
            opp_time = opp_d
            t_self = self_d
            if (adv, -opp_time, -t_self) > (cand[0], -cand[2], -cand[1]):
                cand = (adv, t_self, opp_time)
        pen = obst_adj_pen(nx, ny)
        key = (cand[0], cand[1], -cand[2], -pen, dx, dy)
        if key > best:
            best = key
            best_dxdy = [dx, dy]

    return best_dxdy