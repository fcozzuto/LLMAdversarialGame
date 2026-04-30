def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            res.append((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my_to_opp = man((sx, sy), (ox, oy))

    if not res:
        # No resource info: advance toward opponent with some lateral spread
        tx = w - 1 if ox > sx else 0
        ty = h - 1 if oy > sy else 0
        best = (0, 0)
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            s = -man((nx, ny), (tx, ty)) + 0.05 * (man((nx, ny), (ox, oy)) - my_to_opp)
            if s > best_s:
                best_s = s
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick likely contested target: resource closest to opponent
    target = min(res, key=lambda r: man((ox, oy), r))
    t_opp = man((ox, oy), target)

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_d = man((nx, ny), target)
        gap = (t_opp - my_d)  # positive if we get closer than opponent currently is
        dist_from_opp = man((nx, ny), (ox, oy))

        # Heuristics: secure target, beat opponent on it, avoid letting them be adjacent too often
        score = gap * 22 - my_d * 1.2
        if (nx, ny) in res:
            score += 900
        # Prefer positions not too close to opponent unless we are already winning the contest
        score += 0.3 * max(0, dist_from_opp - 2) - 0.8 * max(0, 2 - dist_from_opp) 
        # Slight preference to keep moving in the direction of target
        score += 0.02 * (man((sx, sy), target) - man((nx, ny), target))

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]