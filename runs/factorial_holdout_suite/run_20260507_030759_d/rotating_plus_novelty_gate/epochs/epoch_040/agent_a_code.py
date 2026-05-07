def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx != 0 or dy != 0 or True) and inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = (-10**9, -10**9)
        for cx, cy in corners:
            self_d = abs(cx - sx) + abs(cy - sy)
            opp_d = abs(cx - ox) + abs(cy - oy)
            v = (opp_d - self_d, -self_d)
            if v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + dx, sy + dy) in obstacles or not inb(sx + dx, sy + dy):
            return [0, 0]
        return [dx, dy]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = None
    best_score = (-10**9, 10**9, 10**9)
    for rx, ry in resources:
        self_d = abs(rx - sx) + abs(ry - sy)
        opp_d = abs(rx - ox) + abs(ry - oy)
        # Prefer resources we can reach much sooner than opponent; then shorter self distance; then determinism by coordinates
        score = (opp_d - self_d, -self_d, -((rx * 31 + ry) % 997))
        if score > (best_score[0], best_score[1], best_score[2]):
            best_score = (score[0], score[1], score[2])
            best_target = (rx, ry)

    tx, ty = best_target
    # Candidate moves: move toward target, but if blocked, pick legal move that maximizes advantage next step
    primary = (0, 0)
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    primary = (dx0, dy0)

    def next_adv(move):
        nx, ny = sx + move[0], sy + move[1]
        self_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        return (opp_d - self_d, -self_d)

    if primary in legal:
        return [primary[0], primary[1]]

    bestm = None
    bestv = (-10**9, -10**9)
    # Deterministic tie-break by move ordering
    for mv in sorted(legal, key=lambda t: (t[0], t[1])):
        v = next_adv(mv)
        if v > bestv:
            bestv = v
            bestm = mv
    return [bestm[0], bestm[1]]