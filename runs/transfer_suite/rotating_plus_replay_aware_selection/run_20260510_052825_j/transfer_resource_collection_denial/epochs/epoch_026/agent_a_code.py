def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick the resource with best advantage (reach sooner than opponent) with urgency.
    tr = observation.get("turns_remaining", 0)
    few = tr <= 6 or observation.get("remaining_resource_count", len(resources)) <= 3
    best_val = None
    target = None
    for rx, ry in resources:
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Advantage with urgency and tie-breaking for nearer-to-self when few remain.
        val = (od - sd) * 2.0 - sd * (0.25 if few else 0.55)
        if sd <= 1:
            val += 4.0
        # Prefer reducing opponent's tempo even when advantage is small.
        if few:
            val += (-sd) * 0.15
        if best_val is None or val > best_val:
            best_val = val
            target = (rx, ry)

    if target is None:
        return [0, 0]
    tx, ty = target

    # Choose best local move (8-way) that heads toward target and avoids obstacles.
    best_score = None
    best_move = [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = man(nx, ny, tx, ty)
            # Small bias to keep movement decisive and to avoid dithering.
            step_bias = 0.0 if (dx == 0 and dy == 0) else -0.05
            # Encourage moving to states that keep advantage over opponent (soft).
            opp_soft = man(ox, oy, tx, ty) - d
            score = d + (0.3 if opp_soft < 0 else -0.1) + step_bias
            if best_score is None or score < best_score:
                best_score = score
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]