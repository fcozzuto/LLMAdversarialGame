def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    opp_dists = {r: man((ox, oy), r) for r in resources}

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        new_d = (nx, ny)

        # Primary: get closer to some remaining resource
        my_best = min((man(new_d, r) for r in resources), default=10**9)

        # Secondary: if we can become closer than opponent for a resource, reward it
        win_margin = 0
        nearest_r = None
        for r in resources:
            d = man(new_d, r)
            m = opp_dists[r] - d
            if m > win_margin:
                win_margin = m
                nearest_r = r

        # Tertiary: avoid getting too close to opponent unless we are winning on a resource
        close_to_opp = man(new_d, (ox, oy))

        # Deterministic tie-break: prefer smaller my_best, then lexicographic position
        score = (
            -my_best,
            win_margin,
            -close_to_opp if win_margin <= 0 else close_to_opp,
            -man(new_d, nearest_r) if nearest_r else 0,
            nx,
            ny,
            dx,
            dy,
        )

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]