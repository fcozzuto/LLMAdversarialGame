def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_sd = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            sd = abs(nx - cx) + abs(ny - cy) + 0.001 * ((nx - sx) ** 2 + (ny - sy) ** 2)
            if best is None or sd < best_sd:
                best_sd = sd
                best = [dx, dy]
        return best if best is not None else [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = [0, 0]
    best_val = None
    best_tiebreak = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Choose best target after this move, but reward being ahead of opponent toward it.
        local_best = None
        local_target = None
        for tx, ty in resources:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            # Margin first (want opd - myd), then prefer shorter myd.
            val = (opd - myd, -myd)
            if local_best is None or val > local_best:
                local_best = val
                local_target = (tx, ty)

        tx, ty = local_target
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        tie_dist = myd + 0.25 * (abs(nx - ox) + abs(ny - oy))
        # Slight preference for progressing toward the chosen resource.
        step_progress = (1 if (nx != tx or ny != ty) else 0) * (abs(tx - sx) + abs(ty - sy) - myd)

        score = (opd - myd) * 100 - myd + step_progress - 0.01 * tie_dist
        tiebreak = (-(opd - myd), myd, abs(dx) + abs(dy), (nx - sx) * (ny - sy))

        if best_val is None or score > best_val or (score == best_val and tiebreak < best_tiebreak):
            best_val = score
            best_tiebreak = tiebreak
            best_move = [dx, dy]

    return best_move