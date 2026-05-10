def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    opp_list = list(opp)
    if not opp_list:
        # If opponent territory unknown, expand toward center and unclaimed.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (-10**18, [0, 0])
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
                continue
            base = 0
            if (nx, ny) in unclaimed:
                base += 5
            elif (nx, ny) in selft:
                base += 1
            distc = abs(nx - cx) + abs(ny - cy)
            val = base * 100 - distc
            if val > best[0]:
                best = (val, [dx, dy])
        return best[1]

    def min_opp_dist(nx, ny):
        md = 10**9
        for px, py in opp_list:
            d = abs(px - nx) + abs(py - ny)
            if d < md:
                md = d
        return md

    # Prefer flipping/marginal expansion near the opponent edge; avoid obstacles.
    # Deterministic tie-break: fixed dir order.
    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        if (nx, ny) in opp:
            cell_score = 6.5
        elif (nx, ny) in unclaimed:
            cell_score = 3.5
        elif (nx, ny) in selft:
            cell_score = 1.5
        else:
            cell_score = 0.5

        # Encourage moving toward the nearest opponent territory.
        d = min_opp_dist(nx, ny)
        toward = 3.0 / (1 + d)

        # Small nudge to avoid bouncing into obstacle-adjacent cells.
        adj_obs = 0
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox == 0 and oy == 0:
                    continue
                if (nx + ox, ny + oy) in obs:
                    adj_obs += 1
        risk = 0.05 * adj_obs

        # Encourage staying near where we already are (reduces oscillations).
        stay_bonus = 0.2 if (nx, ny) in selft else 0.0

        val = cell_score + toward + stay_bonus - risk - 0.01 * (abs(dx) + abs(dy))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move