def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def best_value(px, py):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = md(px, py, rx, ry)
            od = md(ox, oy, rx, ry)
            # Counter sweep_rows: devalue resources on opponent's current row and generally near it
            row_pen = 3 if ry == oy else 0
            row_pen += 2 if abs(ry - oy) == 1 else 0
            # Also bias to keep our y moving away from opponent's sweeping line
            y_away = abs(py - oy)
            val = (od - sd) + y_away * 0.01 - row_pen * 0.5
            # tie-break: prefer shorter self distance
            key = (val, -sd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[0][0] if best is not None else -10**9

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_mv = None
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = best_value(nx, ny)
        # Secondary: progress towards nearest resource (deterministic tie-break)
        dmin = 10**9
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = md(nx, ny, rx, ry)
            if d < dmin:
                dmin = d
        key = (val, -dmin, abs((sx + dx) - ox) - abs(sx - ox), abs((sy + dy) - oy) - abs(sy - oy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    if best_mv is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]