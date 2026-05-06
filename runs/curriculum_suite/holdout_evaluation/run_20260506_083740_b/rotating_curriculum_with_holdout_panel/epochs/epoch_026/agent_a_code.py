def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        tx, ty = (w - 1, h - 1) if (sx + sy) < (w - 1 + h - 1 - sx - sy) else (0, 0)
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mdx, mdy in moves:
            nx, ny = sx + mdx, sy + mdy
            if valid(nx, ny):
                return [mdx, mdy]
        return [0, 0]

    best_val = -10**18
    best_move = (0, 0)
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        cur_best = -10**18
        for rx, ry in resources:
            self_d = d((nx, ny), (rx, ry))
            opp_d = d((ox, oy), (rx, ry))
            # Counter "sweep_rows": avoid opponent's current row unless it creates a big lead.
            row_bias = abs(ry - oy)
            lead = opp_d - self_d
            val = lead + 0.35 * row_bias
            # Small tie-break: prefer reducing Manhattan distance
            val += 0.01 * (-(self_d))
            if val > cur_best:
                cur_best = val
        # Prefer moves that improve the score materially
        if cur_best > best_val:
            best_val = cur_best
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]