def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                if (x, y) not in obs:
                    res.append((x, y))

    if (sx, sy) in obs:
        sx, sy = sx, sy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Choose best target resource by "lead": (opp_dist - self_dist), tie-break by proximity to us.
    if not res:
        tx, ty = (w - 1 + sx) // 2, (h - 1 + sy) // 2
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = -md(nx, ny, tx, ty) - 0.01 * md(nx, ny, ox, oy)
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    best_targets = []
    for tx, ty in res:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        lead = do - ds
        best_targets.append((lead, -ds, tx, ty))
    best_targets.sort(reverse=True)
    target = best_targets[0][2], best_targets[0][3]
    tx, ty = target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # primary: move toward target; secondary: maintain/extend lead vs opponent; tertiary: avoid getting too close to opponent
        my_dist = md(nx, ny, tx, ty)
        opp_dist = md(ox, oy, tx, ty)
        my_cur_dist = md(sx, sy, tx, ty)
        cur_lead = opp_dist - my_cur_dist
        new_lead = opp_dist - my_dist
        block = 1.5 if md(nx, ny, ox, oy) < md(sx, sy, ox, oy) else 0.0
        score = (-my_dist) + 0.8 * (new_lead) + block - 0.01 * md(nx, ny, ox, oy) + 0.001 * (cur_lead)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]