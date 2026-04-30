def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def adj_obstacle_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 1
        return pen

    def score_for_pos(x, y):
        if (x, y) in obstacles:
            return -10**9
        center_bias = -md((x, y), ((w - 1) // 2, (h - 1) // 2)) * 0.05
        if (x, y) in resources:
            return 10000 + center_bias - adj_obstacle_pen(x, y) * 2
        if not resources:
            return center_bias - md((x, y), ((w - 1) // 2, (h - 1) // 2)) * 0.02
        best = -10**9
        for r in resources:
            myd = md((x, y), r)
            opd = md((ox, oy), r)
            # Prefer resources we can secure first; otherwise prefer resources that reduce opponent lead.
            contest = (opd - myd)
            # Convert into a smooth value that strongly rewards "I'm earlier".
            secure = 200 if myd + 1 < opd else 0
            # Also slightly prefer being closer overall (even when contested).
            val = secure + contest * 12 - myd * 1.5 - md((sx, sy), r) * 0.01
            if val > best:
                best = val
        return best + center_bias - adj_obstacle_pen(x, y) * 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = score_for_pos(nx, ny)
        # Deterministic tie-break: smallest (dx,dy) in lexicographic order.
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]