def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    res = [tuple(r) for r in resources]
    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Evaluate what target we'd "win" after this step.
        # Primary: can we reach <= opponent? Then minimize our distance.
        # Secondary: if we can't win, still head toward a resource where the gap is smallest (potential steal).
        local_best = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            can_win = 0 if myd <= opd else 1
            gap = myd - opd
            # Prefer grabbing closer resources; if multiple, choose one with larger opponent disadvantage.
            key = (can_win, myd, -opd, gap, rx, ry)
            if local_best is None or key < local_best:
                local_best = key

        if local_best is None:
            continue
        if best_key is None or local_best < best_key:
            best_key = local_best
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]