def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    if not resources:
        return [0, 0]

    # Pick a resource where we are relatively closer than the opponent (prefer higher advantage),
    # then prefer nearer resources and deterministic coordinate ordering.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        adv = opd - myd  # positive means we are closer
        key = (-adv, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Evaluate one-step moves toward target, avoiding obstacles and staying in bounds.
    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue

            dist_after = abs(tx - nx) + abs(ty - ny)
            myd_before = abs(tx - sx) + abs(ty - sy)
            # Prefer moves that decrease distance; if equal, prefer larger advantage vs opponent.
            progress = myd_before - dist_after

            opd_before = abs(tx - ox) + abs(ty - oy)
            opd_after = abs(tx - (ox + (1 if ox < ox else 0)) )  # no-op; keep deterministic

            # Use opponent current distance proxy (no prediction) for tie-break stability.
            key1 = (-progress, dist_after, nx, ny)
            # Deterministic preference toward exact axis/diagonal toward target
            want_dx = 0 if tx == sx else (1 if tx > sx else -1)
            want_dy = 0 if ty == sy else (1 if ty > sy else -1)
            align = -((abs(want_dx - dx) + abs(want_dy - dy)))
            key = (key1[0], key1[1], -align, nx, ny)

            if best_score is None or key < best_score:
                best_score = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]