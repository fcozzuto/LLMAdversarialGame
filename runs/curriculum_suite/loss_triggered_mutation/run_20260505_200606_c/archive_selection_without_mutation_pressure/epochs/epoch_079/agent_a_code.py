def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (p[0], p[1])
            if t not in obstacles:
                resources.append(t)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def legal(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return (nx, ny)

    best_move = (0, 0)
    best_val = -10**18

    # Current lead map term (for "deny" adjustment)
    cur_best_diff = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        cur_best_diff = max(cur_best_diff, do - ds)

    for dx, dy in moves:
        nxt = legal(sx, sy, dx, dy)
        if nxt is None:
            continue
        nx, ny = nxt
        val = -man(nx, ny, ox, oy) * 0.05  # slight keep-away
        local_best = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            diff = do - ds  # positive means we are closer than opponent
            # If opponent is already much closer to this resource, discourage chasing it unless we can flip lead.
            cur_ds = man(sx, sy, rx, ry)
            cur_do = man(ox, oy, rx, ry)
            opp_closer = 1 if (cur_do + 1 < cur_ds) else 0
            discourage = opp_closer * 2.2 * max(0, (cur_do - cur_ds))
            # Encourage flipping the matchup: diff is key; closer-first tie-break.
            score = 2.4 * diff - 1.0 * ds - discourage
            # If we can create a lead beyond current best, prioritize.
            if diff > cur_best_diff:
                score += (diff - cur_best_diff) * 0.9
            local_best = max(local_best, score)
        val += local_best
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]