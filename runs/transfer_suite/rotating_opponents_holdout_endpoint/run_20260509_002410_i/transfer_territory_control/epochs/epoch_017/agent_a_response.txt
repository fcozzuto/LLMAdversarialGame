def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Frontier heuristic: cells adjacent to opponent territory are high-value targets to disrupt sweeps.
    frontier = set()
    for (x, y) in opp_t:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obstacles:
                frontier.add((nx, ny))

    dist_center = lambda x, y: abs(x - cx) + abs(y - cy)
    dist_opp = lambda x, y: abs(x - ox) + abs(y - oy)

    best = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0

        # Base move preference
        score = 0.0

        if (nx, ny) in opp_t:
            score += 70.0  # flipping opponent territory is strong
        elif (nx, ny) in unclaimed:
            score += 18.0
        elif (nx, ny) in self_t:
            score += 6.0

        # Disruption: prefer entering frontier/near-frontier cells
        if (nx, ny) in frontier:
            score += 22.0
        else:
            # If moving closer to frontier, still reward slightly
            if frontier:
                df = min(abs(nx - fx) + abs(ny - fy) for (fx, fy) in frontier)
                score += (8.0 - df) * 0.8

        # Progress toward center to reduce late-game edge openings
        d0 = dist_center(sx, sy)
        d1 = dist_center(nx, ny)
        score += (d0 - d1) * 2.0

        # Interception: reduce distance to opponent
        score += (dist_opp(sx, sy) - dist_opp(nx, ny)) * 2.8

        # Avoid getting stuck against obstacles: penalize moves that would reduce available neighbors
        if (nx, ny) != (sx, sy):
            free = 0
            for adx, ady in dirs[1:]:
                ax, ay = nx + adx, ny + ady
                if inside(ax, ay) and (ax, ay) not in obstacles:
                    free += 1
            score += free * 0.4

        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best