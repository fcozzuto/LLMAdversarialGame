def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position") or [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Opponent centroid (or fallback to corner) for directional pressure.
    if ot:
        ox = sum(x for x, y in ot) / len(ot)
        oy = sum(y for x, y in ot) / len(ot)
    else:
        ox, oy = (w - 1, h - 1)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_key = (-10**9, None)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        score = 0

        # Immediate flip value: entering opponent-owned cell converts it.
        if (nx, ny) in ot:
            score += 8

        # Claim value: unclaimed cells are likely to add directly.
        if (nx, ny) in unclaimed:
            score += 3

        # Frontier: being adjacent to opponent territory tends to create conversion opportunities.
        adj_opp = False
        for ax, ay in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1),
                       (nx - 1, ny - 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx + 1, ny + 1)):
            if (ax, ay) in ot:
                adj_opp = True
                break
        if adj_opp:
            score += 4
            if (nx, ny) in unclaimed:
                score += 2

        # Keep expanding: slightly prefer moves that are closer to opponent centroid.
        dist = abs(nx - ox) + abs(ny - oy)
        score += max(0, 6 - dist * 0.7)

        # Slightly discourage tight cornering near obstacles.
        near_obst = 0
        for ax, ay in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1),
                       (nx - 1, ny - 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx + 1, ny + 1)):
            if not in_bounds(ax, ay) or (ax, ay) in obstacles:
                near_obst += 1
        score -= near_obst * 0.2

        # Tie-break deterministically by move order preference: smallest (dx,dy).
        key = (score, -1 if (dx, dy) == (0, 0) else 0, -dx, -dy)
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    # If all moves invalid, stay put.
    return [int(best_move[0]), int(best_move[1])]