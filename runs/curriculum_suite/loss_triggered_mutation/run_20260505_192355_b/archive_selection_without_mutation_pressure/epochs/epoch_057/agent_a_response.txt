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

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Primary: secure a resource we can reach no later than opponent (prefer bigger lead).
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd <= od:
            lead = od - sd
            # Tie-break: smaller sd (faster) and farther from opponent (harder to deny after arrival).
            key = (lead, -sd, -od, rx, ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry), sd, od)

    if best is not None:
        rx, ry = best[1]
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        return [dx, dy]

    # Secondary (denial mode): if we can't secure first, move to increase opponent's distance to its closest resource.
    # Deterministic evaluation over our immediate next step.
    opp_best_now = 10**9
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        opp_best_now = min(opp_best_now, md(ox, oy, rx, ry))

    best_move = None
    for dx, dy, nx, ny in moves:
        # Our position blocks by threat: if we're closer to the resource the opponent would take, we can contest.
        # Evaluate: how much our move can increase opponent's "closest contested by us" distance.
        # Define effective opponent distance: for each resource, if we are closer/equal than opponent, treat as high-cost.
        worst = -1
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            od = md(ox, oy, rx, ry)
            sd = md(nx, ny, rx, ry)
            eff = od
            if sd <= od:
                eff += 10  # contested by us
            worst = eff if worst == -1 else min(worst, eff)
        # Prefer moves with larger "worst" (maximize opponent difficulty); tie-break by increasing distance to their nearest resource and moving toward center.
        center_bias = -(abs(3.5 - nx) + abs(3.5 - ny))
        key = (worst, -(opp_best_now), center_bias, dx, dy)
        if best_move is None or key > best_move[0]:
            best_move = (key, (dx, dy))

    return list(best_move[1])