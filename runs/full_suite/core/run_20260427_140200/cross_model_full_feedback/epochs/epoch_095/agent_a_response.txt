def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    def d(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    mep = (mx, my)
    opp = (ox, oy)

    if resources:
        best_t = None
        best_adv = -10**18
        for r in resources:
            myd = d(mep, r)
            opd = d(opp, r)
            adv = myd - opd
            # Prefer resources we can reach sooner (negative adv), then maximize margin we have.
            score = (-adv, -abs(adv), -myd)
            if (best_t is None) or (score > best_adv):
                best_t = r
                best_adv = score

        tx, ty = best_t
        # If opponent is actually closer by a lot, shift to second-best we can still contest.
        # (Deterministic: take resource with best (-adv) among those not too far.)
        if d(opp, (tx, ty)) + 1 < d(mep, (tx, ty)):
            cand = []
            for r in resources:
                adv = d(mep, r) - d(opp, r)
                if adv <= 1:  # at least contestable
                    cand.append((r, (-adv, -d(mep, r), r[0], r[1])))
            if cand:
                cand.sort(key=lambda x: x[1], reverse=True)
                tx, ty = cand[0][0]
    else:
        tx, ty = ox, oy

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not ok(nx, ny):
            continue
        cur = (nx, ny)
        # Main goal: get closer to chosen target.
        my_to = d(cur, (tx, ty))
        # Secondary: deny opponent by minimizing (their distance - ours) after our move.
        op_to = d(opp, (tx, ty))
        deny = (op_to - my_to)
        # Tertiary: avoid stepping adjacent to opponent unless it improves deny.
        adj = 1 if d(cur, opp) <= 2 else 0
        # Small bias to progress toward center to reduce stalls.
        center = (w//2, h//2)
        cent = -d(cur, center) // 2
        val = (deny * 1000) - (my_to * 5) + cent - adj * (1 if deny < 0 else 0)
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]