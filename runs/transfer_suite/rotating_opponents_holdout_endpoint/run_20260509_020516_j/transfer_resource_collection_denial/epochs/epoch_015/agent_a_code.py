def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    best_key = None
    best = None

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Heuristic:
    # 1) Prefer resources where we are closer than opponent (large negative advantage).
    # 2) Penalize targets on/opponent-row or with same "sweep direction" risk.
    # 3) Prefer nearer and more central when ties.
    for rx, ry in resources:
        if (rx, ry) in obstacles or not inside(rx, ry):
            continue
        myd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)

        # Estimate sweep risk: opponent tends to traverse within a row; being on same y is risky.
        row_risk = 0
        if ry == oy:
            row_risk = 6
        # Also mildly avoid cells directly "ahead" along the opponent-to-center vertical tendency.
        col_center_bias = -(((rx - cx0) * (rx - cx0)) + ((ry - cy0) * (ry - cy0)))

        # If we cannot reach quickly (or opponent likely grabs), penalize heavily.
        adv = myd - od  # negative is good
        key = (adv + row_risk, myd, -col_center_bias)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Obstacle-aware: try at most 3 deterministic fallbacks toward target.
    options = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
    for mdx, mdy in options:
        nx, ny = sx + mdx, sy + mdy
        if inside(nx, ny):
            return [int(mdx), int(mdy)]

    return [0, 0]