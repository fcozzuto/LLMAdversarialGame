def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    # Choose target resource: prefer ones we can reach earlier than opponent, breaking ties by closeness.
    target = None
    best_key = None
    for rx, ry in resources:
        ds = dist2(sx, sy, rx, ry)
        do = dist2(ox, oy, rx, ry)
        # Key: maximize our advantage (negative means we are farther), then prefer nearer to us, then deterministic by coords.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            target = (rx, ry)

    # If no resources, drift toward opponent's side while keeping away from obstacles.
    if target is None:
        target = ((w - 1) if ox < sx else 0, (h - 1) if oy < sy else 0)

    tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        ds_new = dist2(nx, ny, tx, ty)
        do = dist2(ox, oy, tx, ty)

        # Prefer: reduce distance to target; increase our reach advantage over opponent.
        # Small obstacle/center bias for stability.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 1e-6

        score = (-ds_new + (do - ds_new) * 0.35) + center_bias
        # Deterministic tie-break: smallest (dx,dy) lex among equals.
        tie = (score, dx, dy)
        if best_score is None or tie > best_score:
            best_score = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]