def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    # For each move, score by best intercept (my arrival first) plus a denial term
    # that slightly reduces opponent distance to resources (even if we don't win them all).
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_best = None  # (win_adv, my_sd, opp_od, opp_nearest_sd)
        my_nearest_opp_gap = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            my_sd = man(nx, ny, rx, ry)
            opp_od = man(ox, oy, rx, ry)
            gap = opp_od - my_sd  # positive means I arrive no later than opponent
            if my_best is None or (gap, -my_sd, -opp_od) > my_best[:3]:
                my_best = (gap, my_sd, opp_od, None)

        # Denial: how close opponent is to the best remaining resource (smaller is better).
        # This encourages moves that prevent opponent from comfortably securing resources.
        opp_nearest = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            d = man(ox, oy, rx, ry)
            if opp_nearest is None or d < opp_nearest:
                opp_nearest = d
        if my_best is None:
            continue
        gap, my_sd, opp_od, _ = my_best

        # Secondary preference: if we can't beat anyone soon, move toward a resource
        # that also keeps opponent farther away (stabilizes vs denier).
        my_nearest_opp_gap = min((man(nx, ny, r[0], r[1]) - man(ox, oy, r[0], r[1]) for r in resources if r and len(r) >= 2), default=0)

        score_key = (gap, -my_sd, -opp_od, -(opp_nearest if opp_nearest is not None else 0), my_nearest_opp_gap)
        if best is None or score_key > best[0]:
            best = (score_key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]