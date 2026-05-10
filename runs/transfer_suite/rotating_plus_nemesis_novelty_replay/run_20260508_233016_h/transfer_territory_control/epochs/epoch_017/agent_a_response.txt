def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = list(observation.get("unclaimed_cells") or [])
    oppx, oppy = observation["opponent_position"]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_value(c):
        # Prefer unclaimed that are promising: far from opponent (harder to contest), but reachable soon.
        ds = man((sx, sy), c)
        do = man((oppx, oppy), c)
        # Slight bias toward edge cells early to limit opponent options.
        edge_bias = 0.25 if (c[0] in (0, w - 1) or c[1] in (0, h - 1)) else 0.0
        return (do - 0.7 * ds) + edge_bias

    if unclaimed:
        # Pick a deterministic "best" target; tie-break by lexicographic cell coords.
        target = max(unclaimed, key=lambda c: (cell_value(c), -c[0], -c[1]))
    else:
        # If no unclaimed, aim to pressure by moving toward opponent territory.
        target = (oppx, oppy)

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0
        cell = (nx, ny)

        ds_new = man(cell, target)
        ds_cur = man((sx, sy), target)
        progress = ds_cur - ds_new  # positive is good

        score = 0.0
        if cell in self_terr:
            score += 0.2
        if cell in unclaimed:
            score += 1.6
        if cell in opp_terr:
            # Entering opponent territory can flip; prefer if it advances toward target (disruptive).
            score += 0.9 + 0.15 * progress

        # Avoid getting stuck by discouraging moving away from target too much.
        score += 1.1 * progress
        # Penalize proximity to obstacles: prefer safer squares.
        neigh_obs = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in obstacles:
                neigh_obs += 1
        score -= 0.05 * neigh_obs

        # Tie-break deterministically.
        key = (score, -abs(dx), -abs(dy), dx, dy)
        if key > best:
            best = key
            best_move = [dx, dy]

    return best_move