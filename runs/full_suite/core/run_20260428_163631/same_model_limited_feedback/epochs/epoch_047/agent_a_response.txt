def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources visible, move toward opponent while avoiding obstacles
    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        # Score preference: closer to our distance, farther from opponent distance
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d1 = dist((sx, sy), (rx, ry))
            d2 = dist((ox, oy), (rx, ry))
            # tie-break by deterministic ordering
            key = (d1 - 0.7 * d2, d1, (rx, ry))
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]

    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    candidates = []
    # Primary: diagonal/axis step toward target
    candidates.append((dx, dy))
    # Secondary: move on one axis
    candidates.append((dx, 0))
    candidates.append((0, dy))
    # Tertiary: best of small "detours" that avoid obstacles
    # Deterministic order: down, up, right, left, and then diagonals back toward target
    for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]:
        if (ddx, ddy) not in candidates:
            candidates.append((ddx, ddy))

    def is_blocked(step):
        nsx, nsy = sx + step[0], sy + step[1]
        return (not in_bounds(nsx, nsy)) or ((nsx, nsy) in obstacles)

    # Choose first non-blocked candidate that also doesn't let opponent immediately capture "more"
    best_step = (0, 0)
    best_eval = None
    for step in candidates:
        if is_blocked(step):
            continue
        ns = (sx + step[0], sy + step[1])
        # Evaluate next position by same heuristic; include tiny preference for approaching target
        if resources:
            eval_best = None
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d1 = dist(ns, (rx, ry))
                d2 = dist((ox, oy), (rx, ry))
                key = (d1 - 0.7 * d2, d1, (rx, ry))
                if eval_best is None or key < eval_best:
                    eval_best = key
            ev = eval_best
        else:
            ev = (dist(ns, (ox, oy)), ns)
        if best_eval is None or ev < best_eval:
            best_eval = ev
            best_step = step

    return [int(best_step[0]), int(best_step[1])]