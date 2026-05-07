def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def cell_score(px, py):
        if not resources:
            return 0.0
        best = -10**18
        for rx, ry in resources:
            sd = man(px, py, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive if we are closer
            time_w = 1.0 + (0.6 if turns_remaining <= 8 else 0.0) - 0.05 * sd
            s = (adv * 2.2) + (od * 0.03) - (sd * 0.12) + time_w * 0.01
            if s > best:
                best = s
        return best

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        cx, cy = w // 2, h // 2
        bestm = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
                continue
            v = -man(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    # One-step lookahead: choose move that maximizes our best achievable resource advantage.
    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obst:
            continue
        v = cell_score(nx, ny)

        # Small tie-break: prefer moves that reduce our distance to the currently best resource.
        # (deterministic without searching paths)
        if v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]