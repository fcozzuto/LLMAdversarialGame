def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0: d1 = -d1
        d2 = ay - by
        if d2 < 0: d2 = -d2
        return d1 + d2

    def step_towards(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        # Try to reduce Manhattan; diagonal is allowed.
        return [x + dx, y + dy]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # Evaluate by best contested resource advantage after this move,
        # with tie-break toward reducing our absolute distance and heading to a resource.
        best_adv = -10**9
        best_self_d = 10**9
        best_threat = -10**9

        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)

            # Model opponent next step as moving one unit toward the same target (greedy).
            ptx, pty = step_towards(ox, oy, rx, ry)
            if ptx < 0 or ptx >= w or pty < 0 or pty >= h or (ptx, pty) in obs:
                ptx, pty = ox, oy
            opd2 = man(ptx, pty, rx, ry)

            # If we are closer than opponent after their greedy move, that's primary.
            adv = (opd2 - myd)
            if adv > best_adv:
                best_adv = adv
                best_self_d = myd
                # If we can "steal" multiple turns, prefer resources that are also close to the opponent.
                best_threat = (opd2 - myd)
            elif adv == best_adv:
                if myd < best_self_d:
                    best_self_d = myd
                    best_threat = (opd2 - myd)

        # Strongly reward being strictly closer; otherwise prioritize smallest my distance
        # and also avoid moves that let opponent have large lead.
        strict = 1 if best_adv > 0 else 0
        val = (strict, best_adv, -best_self_d, -best_threat)
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move