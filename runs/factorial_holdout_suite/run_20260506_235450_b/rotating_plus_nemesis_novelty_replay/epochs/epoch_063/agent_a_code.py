def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
            obstacles.add((x, y))
        except:
            pass

    ox, oy = observation.get("opponent_position", (None, None))
    opp_exists = (ox is not None and oy is not None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        try:
            x, y = r
            res.append((x, y))
        except:
            pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose best resource to contest: minimize (self_dist - opp_adv), where opp_adv favors our lead.
    def target_score(rx, ry):
        sd = man(sx, sy, rx, ry)
        if not opp_exists:
            return sd
        od = man(ox, oy, rx, ry)
        # If opponent is much closer than us, discourage; if we are closer, encourage.
        return sd + (0.7 * (od - sd))

    if res:
        # Deterministically pick the best resource by score, then by coordinates
        best = None
        for rx, ry in res:
            ts = target_score(rx, ry)
            key = (ts, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (sx, sy)

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd2 = man(nx, ny, tx, ty)

        # Secondary objective: don't step into squares that make opponent much closer to any resource.
        opp_pen = 0
        if opp_exists and res:
            best_op = None
            for rx, ry in res:
                d_opp = man(ox, oy, rx, ry)
                # consider how our move affects contested closeness
                d_self = man(nx, ny, rx, ry)
                lead = d_opp - d_self
                # If we are likely to fall behind (lead positive), penalize.
                # If we are likely to gain/maintain lead (lead non-positive), small reward.
                v = lead
                if best_op is None or v < best_op:
                    best_op = v
            if best_op is not None:
                opp_pen = 0.35 * best_op

        # Primary: progress; tie-break: avoid being too far from any immediate resource by minimizing distance to nearest.
        near_self = None
        for rx, ry in (res if res else [(tx, ty)]):
            d = man(nx, ny, rx, ry)
            if near_self is None or d < near_self:
                near_self = d

        val = (sd2, -opp_pen, near_self, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    # If all moves invalid (shouldn't happen), stay.
    return [int(best_move[0]), int(best_move[1])]