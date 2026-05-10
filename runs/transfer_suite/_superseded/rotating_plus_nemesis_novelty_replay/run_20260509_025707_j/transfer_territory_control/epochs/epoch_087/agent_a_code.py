def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    res = set((p[0], p[1]) for p in (observation.get("resources") or []))

    candidates = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        score = -dist
        if (nx, ny) in res:
            score += 5
        if observation.get("remaining_resource_count", 0) and (nx, ny) in res:
            score += 2
        # Tie-break deterministically: prefer moves with smaller dx then dy, then closer to opponent
        tie = (score, -dist, dx, dy)
        if best_score is None or tie > (best_score, -best_dist, best[0], best[1]):
            best = (dx, dy)
            best_score = score
            best_dist = dist

    if best is None:
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]