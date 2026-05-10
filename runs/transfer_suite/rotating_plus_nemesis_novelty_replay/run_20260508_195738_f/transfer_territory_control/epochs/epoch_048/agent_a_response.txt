def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    targets = opp if opp else unclaimed
    if not targets:
        return [0, 0]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Closest target distance from current position (for "progress")
    def manhattan_to_set(px, py, s):
        md = 10**9
        for tx, ty in s:
            d = abs(tx - px) + abs(ty - py)
            if d < md:
                md = d
        return md

    base_dist = manhattan_to_set(x, y, targets)

    best = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        dist = manhattan_to_set(nx, ny, targets)
        progress = base_dist - dist  # positive is good

        opp_here = 1 if (nx, ny) in opp else 0
        claim_here = 1 if (nx, ny) in unclaimed else 0

        # Encourage attacking/expanding frontiers: neighbors near opponent territory
        adj_opp = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in opp:
                    adj_opp += 1

        # Slight preference to stay/expand from our own territory if close
        adj_self = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay) and (ax, ay) in selft:
                    adj_self += 1

        # Deterministic tie-breakers: higher score, then smaller dist, then fixed direction order
        score_tuple = (10 * opp_here + 3 * claim_here + 2 * adj_opp + adj_self + progress, -dist, -dx, -dy)
        if best is None or score_tuple > best[0]:
            best = (score_tuple, dx, dy)

    return [best[1], best[2]] if best else [0, 0]