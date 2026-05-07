def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    moves.sort()
    if not moves:
        return [0, 0]

    if not resources:
        tx = w // 4
        ty = h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - tx) + abs(ny - ty)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer moves that maximize our arrival advantage vs resources, robustly.
    # Robustness: consider top 3 resources by "attractiveness" from our current state,
    # then maximize the minimum advantage across them.
    scored = []
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        advantage = od - sd  # positive => we get there earlier (or deny).
        dist_pen = sd
        scored.append((advantage * 10 - dist_pen, advantage, sd, rx, ry))
    scored.sort(reverse=True)
    top = scored[:3] if len(scored) >= 3 else scored

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        worst_adv = 10**9
        tie_dist = 0
        for _, _, _, rx, ry in top:
            sd2 = man(nx, ny, rx, ry)
            od2 = man(ox, oy, rx, ry)
            adv2 = od2 - sd2
            if adv2 < worst_adv:
                worst_adv = adv2
            tie_dist += sd2
        # Add slight secondary preference for decreasing total distance to the chosen targets.
        cand = (-worst_adv, tie_dist, dx, dy)
        if best is None or cand < best:
            best = cand

    return [best[2], best[3]]