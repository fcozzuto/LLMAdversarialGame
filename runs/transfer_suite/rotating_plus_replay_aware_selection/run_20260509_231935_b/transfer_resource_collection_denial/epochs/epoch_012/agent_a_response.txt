def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))

    # If no visible resources, drift to center while avoiding obstacles.
    if not resources:
        cx, cy = w // 2, h // 2
        bestd = 10**9
        best = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d = dist8(nx, ny, cx, cy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Score resources to deny: prefer ones where we're closer than opponent.
    # Score uses my proximity, my lead over opponent, and slight tie-break by absolute closeness.
    k_lead = 2.2
    k_opp_dist = 0.35
    k_time = 0.02 * (turns_remaining if turns_remaining else 0)

    best_score = -10**30
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Evaluate the best resource from the candidate next position.
        local_best = -10**30
        for rx, ry in resources:
            d_my = dist8(nx, ny, rx, ry)
            d_opp = dist8(ox, oy, rx, ry)
            # Prefer immediate collections too.
            immediate = 20 if d_my == 0 else 0
            # Lead-based priority: maximize (opp - my) to beat denier.
            lead = (d_opp - d_my)
            # Slightly encourage overall progress and discourage long detours.
            val = immediate + k_lead * lead - k_opp_dist * d_my + k_time / (1 + d_my)
            if val > local_best:
                local_best = val

        # Small deterministic tie-break: prefer moves that reduce distance to the globally best target.
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)
        elif local_best == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]