def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neigh_count(sset, nx, ny):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in sset:
                    c += 1
        return c

    best = None
    best_score = -10**18
    # Deterministic tie-break: fixed dir order then lexicographic dx,dy
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0.0
        if (nx, ny) in opp:
            score += 1.8
        elif (nx, ny) in unclaimed:
            score += 1.2
        elif (nx, ny) in selft:
            score += 0.25

        # Expand from our territory; avoid stepping into opponent-favorable front
        score += 0.35 * neigh_count(selft, nx, ny)
        score -= 0.30 * neigh_count(opp, nx, ny)

        # Prefer cutting off closer to opponent position while still expanding
        dist_me = abs(nx - ox) + abs(ny - oy)
        score += 0.02 * (w + h - dist_me)

        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]