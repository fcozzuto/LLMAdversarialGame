def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w // 2), (h // 2)
    else:
        best = None
        # Choose resource using a different bias than last epoch: prioritize beating opponent, then closeness, then corner preference.
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            win = do - ds  # positive means we can get there no later (tie favors by points anyway)
            # Corner preference: prefer targets farther from opponent corner (bottom-right for agent A? opponent is opposite)
            corner_pref = (abs(rx - (w - 1)) + abs(ry - (h - 1))) - (abs(rx) + abs(ry))
            key = (win, -ds, corner_pref, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1] if best else (w // 2, h // 2)

    cur_adv = 0
    # Evaluate next-step options with deterministic tie-breaking.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if resources:
            # Use the chosen target, but also ensure we are improving relative to opponent at this target.
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            adv = do - ds
            # Prefer moves that get closer to target (cheb distance decreases), then higher adv, then lexicographic move ordering.
            dist = ds
            step_pref = (abs((nx - tx)) + abs((ny - ty)))
            candidates.append((dist, -adv, step_pref, dx, dy, adv))
        else:
            dist = cheb(nx, ny, tx, ty)
            candidates.append((dist, 0, 0, dx, dy, 0))

    if not candidates:
        return [0, 0]

    # Deterministic pick: minimize distance, then maximize advantage.
    candidates.sort()
    _, _, _, dx, dy, _ = candidates[0]
    return [int(dx), int(dy)]