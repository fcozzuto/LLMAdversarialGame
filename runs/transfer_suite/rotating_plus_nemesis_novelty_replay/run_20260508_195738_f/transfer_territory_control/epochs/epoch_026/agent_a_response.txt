def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def neigh(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    ax, ay = nx + dx, ny + dy
                    if inb(ax, ay): yield ax, ay

    # If nothing to claim, just head toward opponent territory (or stay if already boxed)
    if not unclaimed and opp:
        bestd = 10**9
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny) or (nx, ny) in obs: 
                continue
            if opp:
                d = min(abs(px - nx) + abs(py - ny) for (px, py) in opp)
            else:
                d = 0
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in opp:
            score += 3.5
        elif (nx, ny) in unclaimed:
            score += 2.2
        elif (nx, ny) in selft:
            score += 0.6
        else:
            score += 0.3

        # Local frontier pressure + expansion
        for ax, ay in neigh(nx, ny):
            if (ax, ay) in obs:
                score -= 0.25
            elif (ax, ay) in opp:
                score += 0.22
            elif (ax, ay) in unclaimed:
                score += 0.14
            elif (ax, ay) in selft:
                score += 0.06

        # Slight bias to move closer to opponent if we're not flipping directly
        if (nx, ny) not in opp and opp:
            md = min(abs(px - nx) + abs(py - ny) for (px, py) in opp)
            score += 0.02 * (-md)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]