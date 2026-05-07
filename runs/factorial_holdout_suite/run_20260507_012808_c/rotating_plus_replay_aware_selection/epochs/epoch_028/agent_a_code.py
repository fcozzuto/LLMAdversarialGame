def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    res_set = set((r[0], r[1]) for r in resources)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = (-man(nx, ny, cx, cy), nx, ny)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        immediate = 2000 if (nx, ny) in res_set else 0
        best_over_resources = -10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer resources we can reach first; break ties by closeness and then proximity to opponent (denial).
            val = (od - sd) * 50 - sd + (od == sd) * 3
            if (rx, ry) in res_set:
                val += 50
            if val > best_over_resources:
                best_over_resources = val
        score = (immediate + best_over_resources, -dx, -dy, nx, ny)  # deterministic tie-break
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]