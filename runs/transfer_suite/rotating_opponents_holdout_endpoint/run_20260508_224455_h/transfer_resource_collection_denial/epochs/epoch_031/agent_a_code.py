def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    me = (sx, sy); opp = (ox, oy)

    # Target: where we are competitive vs opponent (prefer dm<=do), then smaller dm, then deterministic tie-break.
    best = None; best_val = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        dm = man(me, (rx, ry)); do = man(opp, (rx, ry))
        val = (0 if dm <= do else 1, dm, -do, rx * 131 + ry * 17)
        if best is None or val < best_val:
            best_val = val; best = (rx, ry)

    if best is None:
        best = tuple(resources[0])

    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0); best_score = None

    # Small tactic vs sweep-row: if opponent is closer to some resource, head to the best resource we can reach sooner.
    # Compute a "threat" if opponent is already very close to any resource.
    threat = None; threat_val = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        do = man(opp, (rx, ry))
        if do <= 2:
            dm = man(me, (rx, ry))
            val = (do, dm, rx * 131 + ry * 17)
            if threat is None or val < threat_val:
                threat_val = val; threat = (rx, ry)
    if threat is not None:
        # If threat is adjacent to opponent and not much farther for us, prioritize it.
        tdm = man(me, threat); tdo = man(opp, threat)
        if tdo <= 2 and tdm <= tdo + 1:
            tx, ty = threat

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        d_to_target = man((nx, ny), (tx, ty))
        d_to_opp = man((nx, ny), opp)

        # Prefer: reduce distance to target; secondarily avoid moving into squares that let opponent get closer to same target.
        opp_next = man((nx, ny), (tx, ty))  # proxy; keep deterministic
        score = (d_to_target, -d_to_opp, opp_next, nx * 131 + ny * 17)

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]