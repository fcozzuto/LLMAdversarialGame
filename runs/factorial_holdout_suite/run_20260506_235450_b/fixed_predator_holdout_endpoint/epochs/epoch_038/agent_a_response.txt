def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    res = [(int(r[0]), int(r[1])) for r in resources]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def step_score(px, py):
        # Prefer moves that keep us on a resource we can contest (self no farther than opponent),
        # otherwise shift to the resource where we most reduce the opponent's advantage.
        best_contest = None
        best_fallback = None
        for rx, ry in res:
            sd = abs(px - rx) + abs(py - ry)
            od = abs(ox - rx) + abs(oy - ry)
            margin = od - sd  # positive means we are closer
            val = (margin, -sd)
            if sd <= od:
                if best_contest is None or val > best_contest:
                    best_contest = val
            else:
                if best_fallback is None or val > best_fallback:
                    best_fallback = val
        return best_contest if best_contest is not None else best_fallback

    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        base = step_score(nx, ny)
        if base is None:
            continue
        # Obstacle aversion: if next to many obstacles, penalize slightly (encourages routes around blocks).
        near = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obstacles:
                    near += 1
        val = (base[0], base[1] - 0.05 * near)
        if best is None or val > best:
            best = val
            best_move = [dx, dy]
    return best_move