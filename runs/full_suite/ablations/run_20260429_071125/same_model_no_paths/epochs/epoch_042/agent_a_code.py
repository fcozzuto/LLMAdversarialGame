def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Choose target that maximizes (my advantage over opponent) and discourages my moves that increase opponent's lead.
    # Deterministic tie-break order by (score, -dist_to_center, -dist_to_opp, dx, dy)
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy, nx, ny in moves:
        # Evaluate best resource for me given this next step.
        # If I'm already closer than opponent to some resource, that resource is very valuable.
        local_best = -10**18
        for tx, ty in resources if resources else [(cx, cy)]:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Advantage: positive means I'm closer/equal.
            adv = opd - myd
            # Prefer finishing soon: lower myd helps.
            finish = 10.0 / (1 + myd)
            # If opponent is also close, penalize giving them an even better path by increasing my distance and letting adv drop.
            opp_press = 2.0 / (1 + abs(opd - myd))
            val = (adv * 5.0) + finish + opp_press

            # If I can capture immediately, dominate.
            if myd == 0:
                val += 1000.0
            # If opponent can capture immediately, strongly avoid paths that worsen my relative position.
            if opd == 0:
                val -= 800.0

            if val > local_best:
                local_best = val

        # Small spatial shaping to diversify (and not just chase nearest).
        dist_center = cheb(nx, ny, cx, cy)
        dist_to_opp = cheb(nx, ny, ox, oy)
        key = (local_best, -dist_center, dist_to_opp, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]