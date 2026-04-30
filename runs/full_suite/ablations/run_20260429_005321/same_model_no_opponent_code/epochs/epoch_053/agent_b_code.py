def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                candidates.append((dx, dy))

    if not candidates or not resources:
        return [0, 0]

    obs_neighbors = []
    for ox1, oy1 in obstacles_list:
        obs_neighbors.append((ox1, oy1))

    best = None
    best_score = -10**18

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy

        min_ds = 10**9
        best_adv = -10**9
        for rx, ry in resources:
            ds = abs(nx - rx) + abs(ny - ry)
            do = abs(ox - rx) + abs(oy - ry)
            if ds < min_ds:
                min_ds = ds
            adv = do - ds
            if adv > best_adv:
                best_adv = adv

        dist_opp = abs(nx - ox) + abs(ny - oy)

        # Penalty for moving near obstacles to avoid getting boxed
        obst_pen = 0
        for ox1, oy1 in obs_neighbors:
            d = abs(nx - ox1) + abs(ny - oy1)
            if d == 0:
                obst_pen -= 10
            elif d == 1:
                obst_pen -= 2
            elif d == 2:
                obst_pen -= 1

        if best_adv >= 0:
            # We can get at least one resource no later than opponent: prioritize that gap and closeness
            score = best_adv * 120 - min_ds + obst_pen
        else:
            # Opponent is closer to everything: prioritize denying by distancing from opponent while still approaching a target
            score = best_adv * 120 - dist_opp - min_ds * 0.25 + obst_pen

        if score > best_score:
            best_score = score
            best = (dx, dy)

    # Deterministic tie-break if needed
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]