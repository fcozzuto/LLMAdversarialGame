def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def clamp1(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        # Deterministic tie-break: resource list order.
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent, and generally closer overall.
            adv = od - sd
            key = (adv, -sd, -(rx + ry))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    dx = clamp1(tx - sx)
    dy = clamp1(ty - sy)

    candidates = []
    # Prefer direct approach, then other directions in deterministic order.
    pref = [(dx, dy)]
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == dx and my == dy:
                continue
            pref.append((mx, my))
    for mx, my in pref:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Candidate scoring toward target, slight incentive to approach opponent if tie.
        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        score = (-dist, opp_dist, mx, my)
        candidates.append((score, (mx, my)))

    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    return [int(candidates[0][1][0]), int(candidates[0][1][1])]