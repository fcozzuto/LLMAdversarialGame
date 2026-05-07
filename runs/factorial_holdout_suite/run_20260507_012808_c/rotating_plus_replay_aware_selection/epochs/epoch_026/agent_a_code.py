def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    res_set = set((r[0], r[1]) for r in resources)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = (dist(nx, ny, ox, oy), -dist(nx, ny, cx, cy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        immediate = 120 if (nx, ny) in res_set else 0
        nearest_gap = -10**9
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            md = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            gap = od - md  # positive if I'm closer
            if gap > nearest_gap:
                nearest_gap = gap
                my_best = md
                opp_best = od
        # Tie-breakers: prefer being closer to a resource than opponent, and slightly away from opponent.
        opp_pressure = -0.15 * dist(nx, ny, ox, oy)
        step_penalty = -0.02 * (abs(dx) + abs(dy))
        score = immediate + nearest_gap - 0.08 * my_best + opp_pressure + step_penalty
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]