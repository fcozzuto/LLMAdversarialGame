def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick a target resource that maximizes our time advantage.
    target = None
    best_adv = -10**18
    if resources:
        for t in resources:
            sd = dist((sx, sy), t)
            od = dist((ox, oy), t)
            # Prefer larger (od-sd). Break ties by favoring smaller sd (closer to us).
            adv = (od - sd) * 1000 - sd
            if adv > best_adv:
                best_adv = adv
                target = t
    else:
        # No visible resources: drift toward center to reduce stalemate.
        target = (w // 2, h // 2)

    tx, ty = target

    # Choose move that improves our approach to target and worsens opponent's.
    # Tie-break deterministically by move order.
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = abs(nx - tx) + abs(ny - ty)
        opd = abs(ox - tx) + abs(oy - ty)

        # If target resource is adjacent, strongly prefer picking it.
        pick_bonus = 0
        if (nx, ny) == (tx, ty):
            pick_bonus = 10**9
        elif myd == 0:
            pick_bonus = 10**8
        elif myd == 1:
            pick_bonus = 5000

        sc = pick_bonus + (opd - myd) * 200 - myd * 2

        # Small extra: avoid stepping near obstacles by penalizing low mobility (deterministic).
        mobility = 0
        for ddx, ddy in moves:
            x2, y2 = nx + ddx, ny + ddy
            if inb(x2, y2):
                mobility += 1
        sc -= (3 - mobility) * 5

        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]