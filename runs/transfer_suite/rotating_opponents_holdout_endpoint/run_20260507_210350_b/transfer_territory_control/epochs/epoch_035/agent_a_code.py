def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    def to_set(v):
        s = set()
        for p in v or []:
            try:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
            except Exception:
                pass
        return s

    obstacles = to_set(observation.get("obstacles"))
    unclaimed = to_set(observation.get("unclaimed_cells"))
    opp_terr = to_set(observation.get("opponent_territory"))
    self_terr = to_set(observation.get("self_territory"))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Build a frontier set: cells we can reach next step that are unclaimed or opponent territory.
    frontier = set()
    for (x, y) in self_terr:
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and ((nx, ny) in unclaimed or (nx, ny) in opp_terr):
                frontier.add((nx, ny))
    if not frontier:
        frontier = unclaimed | opp_terr

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        sc = 0
        # Core priorities
        if (nx, ny) in unclaimed:
            sc += 220
        if (nx, ny) in self_terr:
            sc += 30  # staying on our claim is safe
        if (nx, ny) in opp_terr:
            sc += 260  # flipping on entry

        # Push toward the board center to maximize claimable area
        dist_center = abs(nx - cx) + abs(ny - cy)
        sc += 80 - 8 * dist_center

        # If we can move into frontier, reward it; otherwise move toward nearest frontier.
        if (nx, ny) in frontier:
            sc += 120
        else:
            # nearest frontier distance (small set from frontier; deterministic by iteration order)
            mind = None
            for (fx, fy) in frontier:
                d = abs(fx - nx) + abs(fy - ny)
                if mind is None or d < mind:
                    mind = d
            if mind is None:
                mind = 10**9
            sc += max(-60, 60 - 10 * mind)

        # Avoid stepping into cells that are adjacent to obstacles too tightly (stability)
        adj_obs = 0
        for ddx, ddy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                adj_obs += 1
        sc -= 4 * adj_obs

        # Deterministic tie-break: prefer moves with smallest dx, then dy, then staying still
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]
        elif sc == best_sc:
            cand = [dx, dy]
            if cand[0] < best[0] or (cand[0] == best[0] and cand[1] < best[1]):
                best = cand

    return [int(best[0]), int(best[1])]