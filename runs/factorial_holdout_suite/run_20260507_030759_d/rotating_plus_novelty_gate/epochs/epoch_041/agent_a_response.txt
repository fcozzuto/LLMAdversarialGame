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
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (0, 0)
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best, bestv = corners[0], (-10**9, 0)
        for cx, cy in corners:
            sd = abs(cx - sx) + abs(cy - sy)
            od = abs(cx - ox) + abs(cy - oy)
            v = (od - sd, -sd)
            if v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    # Choose a target where we can arrive earlier than opponent (with slight tie-break bias).
    # Then greedily pick a move that decreases distance to that target.
    bestt, bestv = resources[0], (-10**9, 10**9)
    for tx, ty in resources:
        sd = abs(tx - sx) + abs(ty - sy)
        od = abs(tx - ox) + abs(ty - oy)
        # Larger is better: lead + small penalty for own slowness
        lead = (od - sd)
        v = (lead, -sd)
        if v > bestv:
            bestv = v
            bestt = (tx, ty)

    tx, ty = bestt
    bestm, bestmd = (0, 0), (10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        selfd = abs(tx - nx) + abs(ty - ny)
        oppd = abs(tx - ox) + abs(ty - oy)
        # primary: get closer; secondary: avoid worsening race position too much; tertiary: progress
        mval = (-selfd, (oppd - selfd), -(abs(nx - tx) + abs(ny - ty)))
        if mval > bestmd:
            bestmd = mval
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]