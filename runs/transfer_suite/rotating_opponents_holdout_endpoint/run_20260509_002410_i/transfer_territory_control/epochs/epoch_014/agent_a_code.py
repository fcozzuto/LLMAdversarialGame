def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells") or []))
    resources = set(map(tuple, observation.get("resources") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a deterministic target: unclaimed with tradeoff between progress toward opponent and central control.
    if unclaimed:
        scored = []
        for tx, ty in unclaimed:
            if (tx, ty) in obstacles:
                continue
            d_to_us = abs(tx - sx) + abs(ty - sy)
            d_to_opp = abs(tx - ox) + abs(ty - oy)
            d_to_center = abs(tx - cx) + abs(ty - cy)
            # Prefer reducing distance to opponent, and moving toward center.
            key = d_to_us + 0.35 * d_to_center - 0.25 * d_to_opp
            scored.append((key, ty, tx))
        if scored:
            _, _, tx = min(scored)
            target_x, target_y = scored[0][2], scored[0][1]
        else:
            target_x, target_y = ox, oy
    else:
        target_x, target_y = ox, oy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-(10**18), 0, 0)

    for dx, dy in dirs:
        x, y = sx + dx, sy + dy
        if not inside(x, y) or (x, y) in obstacles:
            continue

        s = 0
        d_target = abs(x - target_x) + abs(y - target_y)
        s += -2.0 * d_target

        if (x, y) in opp_t:
            s += 900  # flipping on entry
        if (x, y) in unclaimed:
            s += 260
        if (x, y) in resources:
            s += 120
        if (x, y) in self_t:
            s += 25

        # Mild preference to approach opponent and center to avoid getting stranded.
        s += -0.18 * (abs(x - ox) + abs(y - oy))
        s += -0.06 * (abs(x - cx) + abs(y - cy))

        # Deterministic tie-break: prefer smaller dx, then smaller dy.
        cand = (s, -abs(dx), -abs(dy), dx, dy)
        if cand > best:
            best = (cand[0], cand[3], cand[4])

    return [int(best[1]), int(best[2])]