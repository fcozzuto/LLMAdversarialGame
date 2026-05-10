def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best target by current advantage
    best_t = None
    best_key = None
    for tx, ty in res:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = sd - od
        key = (adv, sd, od, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t

    # Evaluate immediate move by resulting advantage toward the best target,
    # plus a secondary check for other nearby targets.
    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None
    for mdx, mdy in candidates:
        nx, ny = sx + mdx, sy + mdy
        if nx < 0: nx = 0
        if nx >= w: nx = w - 1
        if ny < 0: ny = 0
        if ny >= h: ny = h - 1
        hit_obs = (nx, ny) in obs

        sd1 = cheb(nx, ny, tx, ty)
        od1 = cheb(ox, oy, tx, ty)
        adv1 = sd1 - od1

        # Small robustness: consider the best among up to 3 closest resources to us
        # (deterministic selection based on current distances).
        near = sorted(res, key=lambda p: cheb(sx, sy, p[0], p[1]))[:3]
        best_adv_near = None
        best_sd_near = None
        for px, py in near:
            sd = cheb(nx, ny, px, py)
            od = cheb(ox, oy, px, py)
            a = sd - od
            if best_adv_near is None or (a, sd, od, px, py) < (best_adv_near, best_sd_near, od, px, py):
                best_adv_near = a
                best_sd_near = sd

        score = (
            1 if hit_obs else 0,
            adv1,
            sd1,
            best_adv_near,
            best_sd_near if best_sd_near is not None else 0,
            mdx,
            mdy,
        )
        if best_score is None or score < best_score:
            best_score = score
            best_move = [mdx, mdy]

    return best_move