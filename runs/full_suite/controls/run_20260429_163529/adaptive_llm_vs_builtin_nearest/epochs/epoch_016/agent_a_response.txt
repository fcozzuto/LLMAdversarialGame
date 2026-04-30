def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = observation.get("resources") or []
    resources = [(int(r[0]), int(r[1])) for r in resources if r and len(r) >= 2]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        ax, ay, bx, by = int(a), int(b), int(c), int(d)
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    cx, cy = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inside(nx, ny):
                continue
            d_ctr = cheb(nx, ny, cx, cy)
            d_opp = cheb(nx, ny, ox, oy)
            v = -d_ctr + 0.2 * d_opp
            if v > bestv:
                bestv = v
                best = [mx, my]
        return best

    best_target = resources[0]
    best_diff = -10**18
    best_selfd = 10**9
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        diff = od - sd
        if diff > best_diff or (diff == best_diff and sd < best_selfd):
            best_diff = diff
            best_selfd = sd
            best_target = (rx, ry)

    tr, tt = best_target
    best = [0, 0]
    bestv = -10**18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            continue
        myd = cheb(nx, ny, tr, tt)
        od = cheb(nx, ny, ox, oy)
        td_opp = cheb(ox, oy, tr, tt)
        center_bias = -0.1 * cheb(nx, ny, cx, cy)
        # Prefer reaching target sooner; also prefer keeping opponent away from our target race.
        v = (-myd) + 0.6 * (td_opp - cheb(ox, oy, tr, tt) + 0) + 0.05 * od + center_bias
        # The middle term simplifies to 0; keep deterministic structure but effective heuristic is:
        v = (-myd) + 0.05 * od + center_bias
        if v > bestv:
            bestv = v
            best = [mx, my]

    return best