def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick move that maximizes our lead over the opponent on the best contestable resource.
    # Lead = opp_dist - our_dist (higher means we are closer to that resource than they are).
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Compute best contest lead from this candidate position.
        best_lead = -10**9
        best_our_d = 10**9
        best_opp_d = 10**9
        for rx, ry in resources:
            od = man(ox, oy, rx, ry)
            nd = man(nx, ny, rx, ry)
            lead = od - nd
            if lead > best_lead or (lead == best_lead and (nd < best_our_d or (nd == best_our_d and od < best_opp_d))):
                best_lead = lead
                best_our_d = nd
                best_opp_d = od

        # Secondary: if no lead, prefer smaller our distance to nearest resource.
        our_min = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < our_min:
                our_min = d

        # Tertiary: prefer moving toward opponent's closest resource to increase interception pressure.
        opp_near = 10**9
        for rx, ry in resources:
            d = man(ox, oy, rx, ry)
            if d < opp_near:
                opp_near = d
        # Use (lead, -our_min, -dx/dy tie) as deterministic key.
        key = (best_lead, -our_min, -opp_near, -abs(dx), -abs(dy))
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]] if best else [0, 0]