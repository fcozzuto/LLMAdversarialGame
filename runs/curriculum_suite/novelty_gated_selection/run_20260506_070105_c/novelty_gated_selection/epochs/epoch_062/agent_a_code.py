def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if o is not None:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        rx, ry = int(r[0]), int(r[1])
        if (rx, ry) not in obstacles:
            resources.append((rx, ry))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            key = (man(ox, oy, nx, ny), -man(ox, oy, sx, sy))
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Pick target that we can contest: prefer resources where opponent is farther than us.
    best_t = resources[0]
    best_k = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        k = (opd - myd, -(abs(myd - opd)), -myd)  # maximize contest advantage, arrive not later
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t

    # Evaluate immediate moves toward target while keeping contest vs opponent.
    best_move = [0, 0]
    best_score = None
    myd0 = man(sx, sy, tx, ty)
    opd0 = man(ox, oy, tx, ty)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        if myd > myd0 + 1:  # discourage moving away unless stuck
            penalty = 2
        else:
            penalty = 0

        # If we can reduce our distance and keep advantage, prefer that.
        score = (opd - myd) + 0.6 * (myd0 - myd) + 0.2 * (opd0 - opd) - penalty

        # Soft-block: avoid stepping into squares that are adjacent to many obstacles (pathing roughness).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        score -= 0.05 * adj_obs

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]