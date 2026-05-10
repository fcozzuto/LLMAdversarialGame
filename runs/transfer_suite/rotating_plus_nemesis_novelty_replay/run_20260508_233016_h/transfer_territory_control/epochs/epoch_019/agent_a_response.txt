def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_terr = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_terr = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))
    opp_pos = tuple(observation["opponent_position"])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors8(x, y):
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                yield nx, ny

    # Prefer unclaimed frontier cells adjacent to opponent territory (edge-claimer nemesis).
    opp_frontier = set()
    for ox, oy in opp_terr:
        for nx, ny in neighbors8(ox, oy):
            if (nx, ny) in unclaimed:
                opp_frontier.add((nx, ny))

    candidates = list(opp_frontier) if opp_frontier else list(unclaimed)
    if not candidates:
        return [0, 0]

    # Score candidate targets deterministically.
    def target_key(c):
        # Higher is better: closer to us; slightly closer to opponent; and adjacent to opponent (if in frontier).
        d_us = man((sx, sy), c)
        d_opp = man(opp_pos, c)
        adj_bonus = 1 if c in opp_frontier else 0
        edge_bonus = 0.3 if (c[0] == 0 or c[0] == w - 1 or c[1] == 0 or c[1] == h - 1) else 0
        return (adj_bonus, edge_bonus, -d_us, -0.1 * d_opp)

    target = max(candidates, key=target_key)

    # Choose best immediate move (1-step evaluation with obstacle avoidance).
    best = (-10**9, [0, 0])
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
            dx, dy = 0, 0
        cell = (nx, ny)

        # Heuristic: move closer to target; capture unclaimed; discourage deep opponent capture unless frontier.
        dist = man(cell, target)
        score = 0.0
        if cell in self_terr:
            score += 0.05
        if cell in unclaimed:
            score += 1.2
        if cell in opp_terr:
            score += -0.6 if cell not in opp_frontier else 0.2
        # Move toward target more strongly than any single cell attribute.
        score += (50.0 / (1 + dist))

        # Slight preference to keep expanding on edges (matches opponent archetype).
        if cell[0] == 0 or cell[0] == w - 1 or cell[1] == 0 or cell[1] == h - 1:
            score += 0.15
        # Avoid clustering around opponent position if already far from target.
        if man(cell, opp_pos) <= 2:
            score -= 0.05 * (man(cell, target))

        if score > best[0]:
            best = (score, [dx, dy])

    return best[1]