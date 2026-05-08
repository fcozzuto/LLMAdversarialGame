def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = (observation.get("self_position") or [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))
    st = set(map(tuple, observation.get("self_territory") or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    # Precompute a cheap "frontier" preference set: unclaimed cells adjacent to opponent territory.
    frontier = set()
    for (x, y) in unclaimed:
        if ((x - 1, y) in ot) or ((x + 1, y) in ot) or ((x, y - 1) in ot) or ((x, y + 1) in ot) or \
           ((x - 1, y - 1) in ot) or ((x + 1, y - 1) in ot) or ((x - 1, y + 1) in ot) or ((x + 1, y + 1) in ot):
            frontier.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Evaluate each possible move deterministically.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        if (nx, ny) in st:
            score += 1
        if (nx, ny) in unclaimed:
            score += 2
        if (nx, ny) in ot:
            score += 5  # flipping on entry is enabled

        # Move toward opponent-frontier and away from being stuck.
        if frontier:
            if (nx, ny) in frontier:
                score += 8
            else:
                # cheap nearest frontier distance estimate by checking a few candidates: extremal by projection
                # deterministic, no randomness, and avoids full-grid search.
                fx = min(frontier, key=lambda p: (abs(p[0] - nx), p[0]))[0]
                fy = min(frontier, key=lambda p: (abs(p[1] - ny), p[1]))[1]
                score += -0.3 * (abs(fx - nx) + abs(fy - ny))
        else:
            score += -0.15 * (abs(nx - cx) + abs(ny - cy))

        # Slightly prefer moves that increase distance from opponent position (avoid sweeper contact),
        # while still allowing frontier captures. This helps prevent repeated flips losing tempo.
        op = (observation.get("opponent_position") or [w - 1, h - 1])[:2]
        ox, oy = op
        score += -0.05 * (abs(ox - nx) + abs(oy - ny))

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]