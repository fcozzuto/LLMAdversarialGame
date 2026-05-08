def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs_set = set((p[0], p[1]) for p in obstacles)

    def dist(a, b, c, d):
        # Manhattan (deterministic, simple)
        return abs(a - c) + abs(b - d)

    if not resources:
        return [0, 0]

    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obs_set:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer resources closer than opponent; otherwise still reduce self distance
        val = (ds - do * 0.6) + (0.001 * (rx + ry))
        if best is None or val < best_val:
            best = (rx, ry)
            best_val = val

    tx, ty = best
    # Candidate moves: move toward target; then fallback to other safe moves with best evaluation
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                candidates.append((dx, dy))

    # Ensure toward direction candidates are considered first
    sx_step = 0 if tx == sx else (1 if tx > sx else -1)
    sy_step = 0 if ty == sy else (1 if ty > sy else -1)
    primary = []
    other = []
    for dx, dy in candidates:
        if dx == sx_step and dy == sy_step:
            primary.append((dx, dy))
        else:
            other.append((dx, dy))
    candidates = primary + other
    if not candidates:
        return [0, 0]

    best_move = None
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        # if we can move onto target, prefer it
        hit = 1 if (nx, ny) == (tx, ty) else 0
        ds = dist(nx, ny, tx, ty)
        do = dist(ox, oy, tx, ty)
        score = -hit * 1000 + ds - do * 0.6 + 0.001 * (nx - ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]