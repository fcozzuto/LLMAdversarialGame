def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    res_set = set((r[0], r[1]) for r in resources)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Immediate pickup is strongest.
        val = 0
        if (nx, ny) in res_set:
            val += 10**9

        # Otherwise choose a target: prefer resources we beat the opponent on, and closer ones.
        # Tie-break deterministically by coordinates.
        local_best = -10**18
        for r in resources:
            tr = (r[0], r[1])
            myd = abs(nx - tr[0]) + abs(ny - tr[1])
            opd = abs(ox - tr[0]) + abs(oy - tr[1])
            # Positive if we are closer; stronger if we are significantly closer.
            gain = (opd - myd)
            target_val = 5000 * gain - 5 * myd
            # Ensure that if we cannot beat it, we still may go for it if close.
            if gain < 0:
                target_val -= 200 * (-gain)
            # Deterministic tiny tie-break: smaller x then y preferred.
            target_val -= 0.001 * (tr[0] * 10 + tr[1])
            if target_val > local_best:
                local_best = target_val

        val += local_best

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move