def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        by = b - d
        if by < 0: by = -by
        return ax if ax >= by else by

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = cheb(nx, ny, ox, oy)  # run from opponent
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Deterministic one-step advantage heuristic
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        on_res = 1 if (nx, ny) in set(resources) else 0
        sd_near = 10**9
        adv_best = -10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            if sd < sd_near:
                sd_near = sd
            od = cheb(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            if adv > adv_best:
                adv_best = adv

        # Also slightly prefer moving toward center and away from being "walled off"
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -abs(nx - cx) - abs(ny - cy)

        v = 1000 * on_res + 10 * adv_best - 2 * sd_near + 0.1 * center_bias
        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best