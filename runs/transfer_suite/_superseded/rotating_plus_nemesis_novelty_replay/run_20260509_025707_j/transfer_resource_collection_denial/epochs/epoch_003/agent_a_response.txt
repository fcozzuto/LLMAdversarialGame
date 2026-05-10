def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    opts = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    # Pick a target resource we can contest (ours closer), but also keep it near.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        adv = od - sd  # higher => we're closer
        # Deterministic tie-break: then shorter self distance, then coordinates
        key = (-adv, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # One-step greedy on move outcome, respecting obstacles.
    best_move = (0, 0)
    best_key = None
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = manh(nx, ny, tx, ty)
        od2 = manh(ox, oy, tx, ty)
        # Prefer moves that keep us closer to the target than the opponent.
        # Also prefer reducing our distance to the target.
        key = (-(od2 - sd2), sd2, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If somehow all moves blocked (should be rare), stay.
    return [int(best_move[0]), int(best_move[1])]