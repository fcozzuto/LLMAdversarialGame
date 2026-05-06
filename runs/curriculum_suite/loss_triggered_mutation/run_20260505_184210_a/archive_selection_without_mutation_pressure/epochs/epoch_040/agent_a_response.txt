def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return (a[0] - b[0]) if (a[0] >= b[0]) else (b[0] - a[0]) + (a[1] - b[1]) if (a[1] >= b[1]) else (b[1] - a[1])

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # deterministic: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bx, by = sx, sy
        best = None
        bestv = None
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            v = max(abs(nx - cx), abs(ny - cy))
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Predict opponent's likely target: resource minimizing their distance now
    opp_target = min(resources, key=lambda c: (man((ox, oy), c), c[0], c[1]))

    # Score candidate moves:
    # - prioritize taking/contesting opponent's likely target
    # - then prioritize a resource where we can become much closer than opponent
    # - also add small intercept pressure when opponent is near
    legal = sorted(legal)
    best = legal[0]
    bestv = None
    near_opp = man((sx, sy), (ox, oy)) <= 2

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        self_pos = (nx, ny)

        # Primary: advantage on predicted target
        self_dt = man(self_pos, opp_target)
        opp_dt = man((ox, oy), opp_target)
        v = (opp_dt - self_dt) * 10

        # Secondary: best swing on any resource
        swing = -10**9
        for r in resources:
            sd = man(self_pos, r)
            od = man((ox, oy), r)
            # prefer states that improve our rank vs opponent
            sv = (od - sd)
            if sv > swing:
                swing = sv
        v += swing * 3

        # Intercept pressure: if opponent is close, head slightly toward them unless it loses the contest
        if near_opp:
            v += -man(self_pos, (ox, oy))

        # Avoid obstacles implicitly via legality; add minimal tie-break toward predicted target direction
        v += -man(self_pos, opp_target) * 0.1

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]