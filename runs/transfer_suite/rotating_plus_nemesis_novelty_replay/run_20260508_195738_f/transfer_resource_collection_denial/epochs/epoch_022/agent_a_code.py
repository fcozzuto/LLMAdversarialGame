def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def step_toward(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = manh(nx, ny, tx, ty)
            # small deterministic tie-break to avoid oscillation: prefer diagonal then x then y
            key = (d, -((dx != 0) and (dy != 0)), -abs(dx), -abs(dy))
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    if not resources:
        # Hold and squeeze opponent by moving toward the opposite corner relative to opponent.
        tx = 0 if ox > sx else (w - 1 if ox < sx else sx)
        ty = 0 if oy > sy else (h - 1 if oy < sy else sy)
        return step_toward(tx, ty)

    best_target = None
    best_val = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)

        # Counter "sweep_rows": prioritize resources on opponent's current row/col
        bias = 0
        if ry == oy:
            bias -= 3
        if rx == ox:
            bias -= 2
        if (rx + ry) % 2 == (sx + sy) % 2:
            bias -= 1  # deterministic parity preference

        # Main objective: beat the opponent on this resource, but not identical to pure interceptor.
        # Use a softened comparison to reduce repeated niche.
        val = (sd - od) + (sd * 0.15) + bias

        if best_val is None or val < best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target
    return step_toward(tx, ty)