def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # Fallback: move toward center while keeping away from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            score = cheb((nx, ny), (cx, cy)) - 0.5 * cheb((nx, ny), (ox, oy))
            if score < best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]] if best[1] is not None else [0, 0]

    # Score candidate move by: reach nearest resource (primary), avoid getting closer to opponent (secondary),
    # and prefer moves that reduce opponent's nearest-resource distance (tertiary).
    best = (10**18, None)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        me = (nx, ny)

        my_d = min(cheb(me, r) for r in resources)
        opp_d = min(cheb((ox, oy), r) for r in resources)
        my_gain = my_d
        opp_next = min(cheb((ox, oy), r) for r in resources)  # baseline (op move unknown)
        # Estimate "contention": if I move to a resource, I deny it; otherwise, discourage paths that get me near
        # resources that are currently closer to opponent.
        deny = 0
        for r in resources:
            if cheb(me, r) < cheb((ox, oy), r):
                deny += 1

        score = (my_gain * 10) - (deny * 2) + (cheb(me, (ox, oy)) * 0.2) - (opp_d * 0.01) - (opp_next * 0.0)
        if score < best[0]:
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]] if best[1] is not None else [0, 0]