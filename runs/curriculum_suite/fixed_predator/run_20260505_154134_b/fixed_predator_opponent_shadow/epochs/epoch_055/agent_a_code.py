def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def nearest_obs_dist(x, y):
        if not obs:
            return 9
        dmin = 9
        for (px, py) in obs:
            d = cheb(x, y, px, py)
            if d < dmin:
                dmin = d
                if dmin == 0:
                    break
        return dmin

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # obstacle risk (deterministic)
        od = nearest_obs_dist(nx, ny)
        risk_pen = 0 if od >= 2 else (3 - od)  # 2->0,1->2,0 not allowed

        local_best = None
        for cx, cy in resources:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # approximate opponent closing by 1 step in Chebyshev metric
            opp_next_d = opp_d - 1
            if opp_next_d < 0:
                opp_next_d = 0
            gain = opp_next_d - self_d  # positive => we are closer next
            key = (gain, -self_d, -cx, -cy)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue
        final_key = (local_best[0], local_best[1], local_best[2], local_best[3], -risk_pen, dx, dy)
        if best_key is None or final_key > best_key:
            best_key = final_key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move