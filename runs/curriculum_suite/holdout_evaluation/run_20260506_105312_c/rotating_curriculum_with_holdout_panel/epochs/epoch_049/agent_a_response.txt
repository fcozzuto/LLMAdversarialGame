def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_penalty(x, y):
        if (x, y) in obs:
            return 10**9
        p = 0
        # small deterministic penalty to discourage stepping near obstacles
        for (ox2, oy2) in obs:
            d = cheb(x, y, ox2, oy2)
            if d == 0:
                return 10**9
            if d == 1:
                p += 3
            elif d == 2:
                p += 1
        return p

    if not resources:
        best = -10**18
        best_mv = [0, 0]
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            # edge_patrol likely, so bias to interior by minimizing distance to center
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center_d = cheb(nx, ny, cx, cy)
            val = -center_d - obs_penalty(nx, ny)
            if val > best:
                best = val
                best_mv = [dx, dy]
        return best_mv

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    # Determine a target regime: go for resources that give the largest distance advantage over opponent.
    best = -10**18
    best_mv = [0, 0]
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        opp_adv_best = -10**18
        my_d_best = 10**9
        my_to_center = cheb(nx, ny, cx, cy)
        for r in resources:
            rx, ry = r[0], r[1]
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            adv = (oppd - myd)  # positive if this cell is closer than opponent to that resource
            if myd < my_d_best:
                my_d_best = myd
            if adv > opp_adv_best:
                opp_adv_best = adv
        val = 4.0 * opp_adv_best - 0.6 * my_d_best - 0.15 * my_to_center - obs_penalty(nx, ny)
        if val > best:
            best = val
            best_mv = [dx, dy]

    return best_mv