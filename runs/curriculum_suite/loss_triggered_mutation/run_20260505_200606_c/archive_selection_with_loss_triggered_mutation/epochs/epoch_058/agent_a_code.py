def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # If we are standing on a resource, stay/adjust minimally.
    if resources:
        if (sx, sy) in set(tuple(r) for r in resources):
            return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 10**9)
        bestm = (0, 0)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            row_pen = 0 if ny != oy else 2
            v = (row_pen, abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy))
            if v < best:
                best = v
                bestm = (mx, my)
        return [bestm[0], bestm[1]]

    res_set = set(tuple(r) for r in resources)
    bestv = None
    bestm = (0, 0)

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer capturing immediately.
        immediate = 0 if (nx, ny) in res_set else 1

        # Choose the resource that gives the best advantage after this move.
        cand_adv = -10**9
        cand_threat = 10**9
        cand_opp_to_block = 10**9
        for rx, ry in res_set:
            se = dist((nx, ny), (rx, ry))
            oe = dist((ox, oy), (rx, ry))
            adv = oe - se  # positive means we are closer than opponent
            if adv > cand_adv or (adv == cand_adv and se < cand_threat):
                cand_adv = adv
                cand_threat = se
                cand_opp_to_block = oe

        # Additional tie-breakers: avoid moving into opponent-favorable immediate proximity.
        opp_adj = max(abs(nx - ox), abs(ny - oy))  # 0..?
        v = (
            immediate,
            -cand_adv,
            cand_threat,
            opp_adj,
            abs(nx - (w - 1) // 2) + abs(ny - (h - 1) // 2),
            (nx, ny),
        )
        if bestv is None or v < bestv:
            bestv = v
            bestm = (mx, my)

    return [int(bestm[0]), int(bestm[1])]