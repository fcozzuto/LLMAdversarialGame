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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource by "race advantage" rather than nearest.
    # Prefer where we are closer than opponent; if none, prefer least disadvantage.
    if resources:
        best_t = None
        best_val = None
        for r in resources:
            myd = dist((sx, sy), r)
            opd = dist((ox, oy), r)
            advantage = opd - myd  # larger is better
            mid_bias = -abs((sx + ox) - 2 * r[0]) - abs((sy + oy) - 2 * r[1])
            # Tie-break deterministically by coordinates
            val = ( -myd, -opd, -(advantage) * -1, -(mid_bias), r[0], r[1])  # crafted to reduce brittleness
            # Convert to: maximize advantage, then minimize my distance, then minimize opponent distance
            score = (-advantage, myd, opd, r[0], r[1])
            if best_val is None or score < best_val:
                best_val = score
                best_t = r
    else:
        best_t = (w - 1 - ox, h - 1 - oy)  # deterministic fallback: chase mirrored corner

    tx, ty = int(best_t[0]), int(best_t[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Step scoring: maximize expected advantage after move; avoid obstacles and bounds.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd2 = dist((nx, ny), (tx, ty))
        # Opponent "pressure": prefer moves that increase our relative closeness to target.
        opd2 = dist((ox, oy), (tx, ty))
        adv = opd2 - myd2
        # Secondary: move toward target; also keep away from obstacles by mild penalty.
        wall_pen = 0
        if nx in (0, w - 1) or ny in (0, h - 1):
            wall_pen = 0.1
        obs_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    obs_adj += 1
        score = (-adv, myd2, opd2, wall_pen + 0.05 * obs_adj, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]