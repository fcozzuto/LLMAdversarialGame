def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Opponent "sweep_rows" tendency: prioritize not letting them take the same-row prizes.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        gain = opd - myd  # positive means we're closer
        row_pen = 3 if ry == oy else 0
        # Mild center pressure to avoid getting stuck in a corner while contesting
        cen = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        # Higher is better; deterministic tie-breaker by (gain, -myd, center, coords)
        key = (gain - row_pen, -myd, -cen, -rx, -ry, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best
    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try alternate step in x/y to avoid obstacle; deterministic.
        if dx != 0 and (sx + dx, sy) not in obstacles:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in obstacles:
            return [0, dy]
        return [0, 0]

    return [dx, dy]