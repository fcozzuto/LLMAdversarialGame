def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Pick a primary target: favor resources that are closer for us and not too close for opponent.
        best_t = None
        best_k = -10**18
        for rx, ry in resources:
            ourd = man(sx, sy, rx, ry)
            oppd = man(ox, oy, rx, ry)
            k = (oppd - ourd) * 200 - ourd * 3 + (rx - 3.5) * 0.2 - ry * 0.1
            if k > best_k:
                best_k = k
                best_t = (rx, ry)
        target = best_t
    else:
        target = (w // 2, h // 2)

    # Interception: if opponent is very close to some resource, aim to reduce the opponent's advantage.
    critical = None
    if resources:
        min_opp = 10**9
        for rx, ry in resources:
            oppd = man(ox, oy, rx, ry)
            if oppd < min_opp:
                min_opp = oppd
                critical = (rx, ry)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Value to our primary target
        tx, ty = target
        our_to_t = man(nx, ny, tx, ty)
        opp_to_t = man(ox, oy, tx, ty)

        val = (opp_to_t - our_to_t) * 250 - our_to_t * 4

        # If critical exists, include an interference term by choosing moves that reduce opp advantage
        if critical is not None:
            cx, cy = critical
            opp_to_c = man(ox, oy, cx, cy)
            our_to_c = man(nx, ny, cx, cy)
            # If opponent is closer, try to "steal" by approaching quickly; otherwise just keep heading to target
            if opp_to_c <= our_to_c:
                val += (opp_to_c - our_to_c) * 180 - our_to_c * 2
            else:
                val += (opp_to_c - our_to_c) * 40

        # Small tie-break to move toward target coordinates deterministically
        val += (nx - tx) * 0.01 + (ny - ty) * 0.005

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]