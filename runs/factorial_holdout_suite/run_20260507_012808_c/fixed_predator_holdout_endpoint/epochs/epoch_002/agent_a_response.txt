def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Simple: move toward center slightly to avoid wasting turns.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = (-10**9, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (-md((nx, ny), (cx, cy)), md((nx, ny), (ox, oy)))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose resource where we can improve the lead: (opp_dist - my_dist) + slight preference for closeness
    best_r = None
    best_s = (-10**18, 10**18)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = md((sx, sy), (rx, ry))
        opd = md((ox, oy), (rx, ry))
        # Primary: bigger lead advantage for us (positive means we are closer). Secondary: shorter my distance.
        s = (opd - myd, -myd)
        if s > best_s:
            best_s = s
            best_r = (rx, ry)

    tx, ty = best_r

    # Move toward target while reducing being “too accessible” to opponent (resource denier archetype)
    best_move = [0, 0]
    best_score = (-10**18, 10**18, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd_next = md((nx, ny), (tx, ty))
        opd_next = md((nx, ny), (ox, oy))

        # Prefer states where we stay closer to target and we are not giving opponent an easy interception.
        lead_now = md((sx, sy), (tx, ty)) - md((ox, oy), (tx, ty))
        lead_next = myd_next - opd_next

        score1 = (-myd_next, -opd_next)          # closer to target, also not adjacent to opponent
        score2 = (-abs(lead_next), -lead_now)    # keep/restore lead relative to opponent
        # Encode lexicographically with a tuple
        v = (score1[0], score1[1], score2[0], score2[1])
        if v > best_score:
            best_score = v
            best_move = [dx, dy]

    return best_move