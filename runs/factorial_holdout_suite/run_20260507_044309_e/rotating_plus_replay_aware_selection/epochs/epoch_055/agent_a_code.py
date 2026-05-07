def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    turns_remaining = observation.get("turns_remaining", 0) or 0

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, cheb(ox, oy, tx, ty))
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Pick resource where we are more likely to arrive first; break ties deterministically.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer higher advantage (opponent slower), then lower our distance, then lower opponent distance.
        # Tie-break: lexicographic by coordinates for determinism.
        adv = do - ds
        key = (-adv, ds, do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = None
    best_move_key = None
    # Greedy step toward target, but allow "staging" when opponent is close: slightly prefer minimizing
    # our distance and also keeping opponent away (by maximizing their distance increase).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        my_improve = cheb(sx, sy, tx, ty) - my_d
        opp_worsen = 0
        # If we can, try to pick move that increases our lead or at least doesn't reduce it.
        # Use turns_remaining to vary tie-breaking deterministically across time.
        k = (my_d, -my_improve, -opp_worsen, (turns_remaining % 3), dx, dy)
        if best_move_key is None or k < best_move_key:
            best_move_key = k
            best_move = [dx, dy]
    return best_move if best_move else [0, 0]