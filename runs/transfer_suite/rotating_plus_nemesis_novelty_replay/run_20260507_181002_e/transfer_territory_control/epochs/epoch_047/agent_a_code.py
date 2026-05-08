def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed:
        resources = toset(observation.get("resources"))
        unclaimed = set(resources) if resources else set()
    if not unclaimed:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    bestv = -10**18
    for tx, ty in unclaimed:
        if (tx, ty) in obstacles:
            continue
        ds = abs(sx - tx) + abs(sy - ty)
        do = abs(ox - tx) + abs(oy - ty)
        if ds == 0:
            score = 1e9
        else:
            center_bias = 0.12 * (abs(tx - cx) + abs(ty - cy)) * -1.0
            # Prefer cells we can reach sooner (territory flip on entry); tie-break by center.
            score = (do - ds) * 100.0 - ds * 1.8 + center_bias
        if score > bestv:
            bestv = score
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Sanity: if that target direction is blocked, try a nearby move that best advances towards target.
    desired = (dx, dy)
    if desired == (0, 0):
        return [0, 0]
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        cand = None
        candv = -10**18
        for mx, my in moves:
            if mx == 0 and my == 0:
                continue
            xx, yy = sx + mx, sy + my
            if not (0 <= xx < w and 0 <= yy < h) or (xx, yy) in obstacles:
                continue
            nds = abs(xx - tx) + abs(yy - ty)
            ndo = abs(xx - ox) + abs(yy - oy)
            v = (ndo - nds) * 100.0 - nds * 1.8 - 0.02 * (abs(xx - cx) + abs(yy - cy))
            if v > candv:
                candv = v
                cand = (mx, my)
        return [cand[0], cand[1]] if cand else [0, 0]

    return [dx, dy]