def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obs.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obs.add((int(p["x"]), int(p["y"])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", None)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                res.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                res.append((int(r["x"]), int(r["y"])))

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_res = None
    best_score = -10**18
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        takeover = 1 if myd <= opd else 0
        dist_term = -(myd) - 0.15 * (myd + 1)  # slight bias to nearer
        score = 1000 * takeover + dist_term
        if score > best_score:
            best_score = score
            best_res = (rx, ry)

    rx, ry = best_res
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            order.append((dx, dy))

    if not order:
        return [0, 0]

    best_move = (0, 0)
    best_move_score = -10**18
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        myd_next = cheb(nx, ny, rx, ry)
        # If step accidentally makes us worse than staying, still allow if it blocks opponent by taking closer resource.
        opp_d_next = cheb(ox, oy, rx, ry)
        takeover = 1 if myd_next <= opp_d_next else 0
        progress = -(myd_next)
        # Favor not moving away from nearest target direction too much
        manh_approx = abs((nx - rx)) + abs((ny - ry))
        move_score = 1000 * takeover + progress - 0.01 * manh_approx
        if move_score > best_move_score:
            best_move_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]