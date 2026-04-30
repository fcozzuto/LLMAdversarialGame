def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = (-1, 0, 1)
    resset = set(resources)

    # If sitting on a resource, do not waste time.
    if (sx, sy) in resset:
        # Move toward next best resource while avoiding obstacles.
        pass

    # Pick a target resource where we are (or will be) faster than opponent.
    best_t = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd)  # higher means we are closer / opponent farther
        if adv > best_adv:
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t

    def obstacle_risk(nx, ny):
        if (nx, ny) in obstacles:
            return 1000
        risk = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (nx + ix, ny + iy) in obstacles:
                    risk += 2
        return risk

    best_move = [0, 0]
    best_score = -10**18

    # Evaluate local moves with deterministic scoring and obstacle avoidance.
    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            myd = cheb(nx, ny, tx, ty)

            # Prefer intercepting when opponent also heads to the same resource:
            opd = cheb(ox, oy, tx, ty)
            intercept_bonus = 0
            if opd > 0:
                # If opponent is close, rush to shrink our remaining distance quickly.
                intercept_bonus = 0.8 * (opd - myd) - 0.2 * myd

            # Avoid obstacles and also prefer staying mobile (not sandwiched).
            risk = obstacle_risk(nx, ny)
            mobility = 0
            for mx in dirs:
                for my in dirs:
                    if mx == 0 and my == 0:
                        continue
                    ax, ay = nx + mx, ny + my
                    if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                        mobility += 1

            # Main objective: minimize distance to target, break ties toward higher mobility, then away from risk.
            score = (-myd * 10) + intercept_bonus * 1.0 + mobility * 0.15 - risk * 3.0