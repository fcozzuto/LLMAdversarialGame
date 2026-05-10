def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource: minimize my distance while maximizing opponent distance (denial).
    best_i = 0
    best_val = None
    for i, (rx, ry) in enumerate(resources):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Bias for resources aligned with opponent to discourage sweep-row races.
        row_bonus = 1.25 if ry == oy else 0.0
        col_bonus = 0.7 if rx == ox else 0.0
        # Extra weight to denial when I'm not already closer.
        rel = 1.0 if sd <= od else 1.35
        val = (sd - 1.2 * rel * od - row_bonus - col_bonus) * 10 + sd
        if best_val is None or val < best_val:
            best_val = val
            best_i = i

    tx, ty = resources[best_i]
    # Desired direction toward target.
    want_dx = 0 if tx == sx else (1 if tx > sx else -1)
    want_dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Among legal moves, choose one that best advances toward target while maintaining denial.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_s = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny):
            continue
        # Advance heuristic
        dist_after = man(nx, ny, tx, ty)
        dist_before = man(sx, sy, tx, ty)
        adv = dist_before - dist_after  # positive is good

        # Denial vs opponent: prefer squares that increase opponent's distance to target.
        od_now = man(ox, oy, tx, ty)
        od_after = man(ox, oy, tx, ty)  # opponent move unknown; use current od only as anchor
        denial = od_after - od_now

        # Alignment with desired direction (tie-break)
        align = -abs(want_dx - mx) - abs(want_dy - my)

        # Slight preference to not give up row when opponent is on same row.
        row_pen = 0.0
        if ty == oy and ny != oy:
            row_pen = 0.35

        score = 100 * adv - dist_after + 0.2 * denial + 0.5 * align - row_pen
        if best_s is None or score > best_s:
            best_s = score
            best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]