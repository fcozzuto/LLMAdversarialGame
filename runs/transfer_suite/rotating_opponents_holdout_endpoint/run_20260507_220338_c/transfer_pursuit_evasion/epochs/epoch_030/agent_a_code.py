def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x, y):
        return abs(x - ox) if abs(x - ox) > abs(y - oy) else abs(y - oy)

    role = str(observation.get("self_role", "pursuer") or "pursuer").lower()
    evade = ("evad" in role) or ("run" in role) or ("away" in role)
    want = 1 if evade else -1

    # 2-ply deterministic lookahead with mobility tie-break to handle wall-running
    best = None
    bestv = None
    for dx, dy in deltas:
        x1, y1 = sx + dx, sy + dy
        if not ok(x1, y1):
            continue

        # mobility from next position
        mob1 = 0
        for adx, ady in deltas:
            if ok(x1 + adx, y1 + ady):
                mob1 += 1

        # approximate "best/worst" after opponent-less dynamics: use our own 1 more step
        # If pursuing: we want to minimize distance; if evading: maximize distance.
        best2 = -10**9 if evade else 10**9
        for adx, ady in deltas:
            x2, y2 = x1 + adx, y1 + ady
            if not ok(x2, y2):
                continue
            v = cheb(x2, y2)
            if evade:
                if v > best2:
                    best2 = v
            else:
                if v < best2:
                    best2 = v
        if best2 == (-10**9 if evade else 10**9):
            best2 = cheb(x1, y1)

        v = want * best2 + (mob1 if evade else mob1 * 0.15)
        if best is None or v > bestv:
            best, bestv = (dx, dy), v

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]