def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            d = cheb(nx, ny, cx, cy) - 0.01 * cheb(nx, ny, ox, oy)
            cand = (d, nx, ny)
            if best is None or cand < best:
                best = cand
        return [best[1] - sx, best[2] - sy]

    # Score resources by how much closer we are than opponent (tie -> nearer to us).
    # Then choose the move that maximizes our advantage and reduces our distance to that target.
    def best_resource(px, py):
        best = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            cand = (-adv, ds, rx, ry)  # we will take min on this
            if best is None or cand < best:
                best = cand
        # unpack: adv stored negated, so compute actual
        rx, ry = best[2], best[3]
        return rx, ry

    tx, ty = best_resource(sx, sy)

    best_score = None
    best_move = (0, 0)

    # Deterministic: fixed tie order by move lexicographic on (dx,dy).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy

        # Evaluate after move: our contested advantage at target, plus global threat against other resources.
        ds_t = cheb(nx, ny, tx, ty)
        do_t = cheb(ox, oy, tx, ty)
        adv_t = do_t - ds_t

        # Also consider whether we "steal" a different resource better.
        # Use a small fixed sample: closest 3 resources by our distance.
        rs = []
        for rx, ry in resources:
            rs.append((cheb(nx, ny, rx, ry), rx, ry))
        rs.sort()
        ds_best_other = rs[0][0]
        adv_best_other = -10**9
        for k in range(3 if len(rs) >= 3 else len(rs)):
            _, rx, ry = rs[k]
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            val = do - ds
            if val > adv_best_other:
                adv_best_other = val
        # Prefer: maximize advantage, then minimize distance to target, then minimize distance to best-other (more efficient).
        score_tuple = (-adv_t, ds_t, ds_best_other, adv_best_other)
        # Convert to comparable with max-like preference via lexicographic on tuple: smaller is better.
        if best_score is None or score_tuple < best_score or (score_tuple == best_score and (dx, dy) < best_move):
            best_score = score_tuple
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]