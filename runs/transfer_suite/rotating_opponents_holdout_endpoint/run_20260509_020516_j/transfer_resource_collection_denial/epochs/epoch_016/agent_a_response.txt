def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_score = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)

        # Prefer resources we can get first; otherwise still prefer large relative advantage.
        adv = od - myd  # positive means we are closer or tie

        # Risk: if opponent is on same row, being too "aligned" tends to lose races.
        row_risk = 0
        if ry == oy:
            row_risk = 5

        # Mildly prefer central cells and avoid very edge cells when not winning races.
        center_bonus = -0.15 * (abs(rx - cx) + abs(ry - cy))
        edge_pen = 0
        if rx in (0, w - 1) or ry in (0, h - 1):
            edge_pen = 0.6

        score = adv * 2.5 + center_bonus - row_risk - (0.25 if adv < 0 else 0) * edge_pen

        # Tie-break: if scores close, choose smaller my distance.
        key = (score, -myd, -(abs(rx - cx) + abs(ry - cy)))
        if best is None or key > best:
            best = key
            best_score = score
            target = (rx, ry)

    tx, ty = target

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Deterministic obstacle-avoidance: if target step is blocked, try alternative on axis priority.
    nx, ny = sx + dx, sy + dy
    if inside(nx, ny):
        return [dx, dy]

    # Try axis moves: prefer the axis that decreases distance most.
    opts = []
    if dx != 0:
        nx1, ny1 = sx + dx, sy
        if inside(nx1, ny1):
            opts.append((abs(tx - (sx + dx)) + abs(ty - sy), [dx, 0]))
    if dy != 0:
        nx2, ny2 = sx, sy + dy
        if inside(nx2, ny2):
            opts.append((abs(tx - sx) + abs(ty - (sy + dy)), [0, dy]))
    # Try diagonal variants (still within one step) deterministically.
    cand = []
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if (ddx, ddy) == (0, 0) or (ddx, ddy) not in ((dx, dy), (dx, 0), (0, dy)):
                continue
            xx, yy = sx + ddx, sy + ddy
            if inside(xx, yy):
                cand.append((abs(tx - xx) + abs(ty - yy), [ddx, ddy]))
    if cand:
        cand.sort()
        return cand[0][1]
    if opts:
        opts.sort()
        return opts[0][1]
    return [0, 0]