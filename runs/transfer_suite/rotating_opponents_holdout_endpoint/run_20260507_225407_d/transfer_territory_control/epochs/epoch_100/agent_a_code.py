def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    self_cells = set(tuple(c) for c in (observation.get("self_territory") or []))
    opp_cells = set(tuple(c) for c in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(c) for c in (observation.get("unclaimed_cells") or []))

    opp_edges = set()
    for (ox, oy) in opp_cells:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = ox + dx, oy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and (nx, ny) in unclaimed:
                    opp_edges.add((nx, ny))
    if not opp_edges:
        opp_edges = set(unclaimed)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opponent_pos = observation.get("opponent_position") or (w - 1, h - 1)
    opponent_pos = (int(opponent_pos[0]), int(opponent_pos[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    opp_near = min([dist((nx, ny), opponent_pos) for (nx, ny) in opp_cells], default=999)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        target_unclaimed_dist = min([dist((nx, ny), t) for t in opp_edges], default=999)
        target_any_unclaimed = min([dist((nx, ny), t) for t in unclaimed], default=999)

        gain = 0.0
        if (nx, ny) in self_cells:
            gain += 0.05
        elif (nx, ny) in unclaimed:
            gain += 1.25  # claim unclaimed aggressively
        elif (nx, ny) in opp_cells:
            gain += 0.95  # flip if it happens

        # Prefer moving toward the nearest unclaimed frontier; penalize lingering.
        score = gain - 0.35 * target_unclaimed_dist - 0.10 * target_any_unclaimed
        # If very close to opponent territory, prioritize flipping instead of strolling.
        if opp_near <= 6:
            if (nx, ny) in opp_cells:
                score += 0.75
            elif (nx, ny) in unclaimed:
                score += 0.15

        # Tie-break deterministically: prefer larger dx then larger dy then stay last.
        if score > best_score or (score == best_score and (dx, dy) > best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]