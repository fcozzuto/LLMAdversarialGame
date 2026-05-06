def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked(x, y):
        return (x, y) in obstacles

    # Prefer a resource where we are relatively closer; if opponent is closer, deny the closest they are targeting.
    scored = []
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        advantage = opd - myd  # positive means we're closer
        urgency = myd + opd
        scored.append((-(advantage), urgency, rx, ry, myd, opd))
    # Deterministic pick: minimal key => best advantage, then best overall urgency.
    _, _, tx, ty, myd, opd = min(scored)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # One-step evaluation: move closer to target, avoid obstacles, and slightly avoid stepping into opponent-closer positions.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if blocked(nx, ny):
            continue
        dist_t = man(nx, ny, tx, ty)

        # Compute opponent pressure on the same target.
        dist_op_t = man(ox, oy, tx, ty)
        dist_op_after = man(ox, oy, tx, ty)  # opponent position unchanged this turn
        _ = dist_op_after

        # Opponent pressure via relative distance swing.
        my_after = man(nx, ny, tx, ty)
        my_now = myd
        swing = my_now - my_after  # positive if we improved closeness

        # Also steer slightly to reduce distance to nearest resource we can actually secure (we assume immediate step only).
        nearest_sec = 10**9
        for rx, ry in resources:
            if man(nx, ny, rx, ry) < nearest_sec:
                nearest_sec = man(nx, ny, rx, ry)

        # Penalty for moving closer to opponent's current diagonal direction: encourage breaking diagonal probe by not mirroring.
        diag_pref = (abs((ox - nx) - (oy - ny)) == 0)  # heuristic: diagonal alignment
        diag_pen = 1 if diag_pref else 0

        val = (dist_t, -swing, nearest_sec, diag_pen)

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move