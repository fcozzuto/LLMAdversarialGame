def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    resset = set(tuple(p) for p in resources)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    scored_targets = []
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        adv = do - ds  # positive => we are closer
        row_focus = 1.0 if ry == oy else 0.0
        col_focus = 0.2 if rx == ox else 0.0
        near = abs(rx - sx) + abs(ry - sy)
        key = (-adv - 0.6 * row_focus - 0.2 * col_focus, near, rx, ry)
        scored_targets.append((key, (rx, ry), adv))
    scored_targets.sort(key=lambda t: t[0])
    targets = [t[1] for t in scored_targets[:3]]

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        move_score = 0
        if (nx, ny) in resset:
            move_score += 10  # immediate collection
        # Prefer increasing our lead to the best contested target(s)
        for (tx, ty) in targets:
            ds2 = abs(tx - nx) + abs(ty - ny)
            do2 = abs(tx - ox) + abs(ty - oy)
            adv2 = do2 - ds2
            row_gain = 1.0 if ty == oy else 0.0
            # Encourage reducing our distance even if we're not currently winning
            dist_pen = ds2 * 0.05 + (0.02 if (tx, ty) in resset else 0)
            move_score += adv2 * 1.5 + row_gain * 0.8 - dist_pen
            # Mild "corridor" pressure: if opponent is sweeping, try to align y while approaching x
            if oy == ny:
                move_score += 0.15 * (1 if abs(tx - nx) < abs(tx - sx) else 0)
        # Deterministic tie-breaker
        if best_score is None or move_score > best_score or (move_score == best_score and (dx, dy) < tuple(best_move)):
            best_score = move_score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]