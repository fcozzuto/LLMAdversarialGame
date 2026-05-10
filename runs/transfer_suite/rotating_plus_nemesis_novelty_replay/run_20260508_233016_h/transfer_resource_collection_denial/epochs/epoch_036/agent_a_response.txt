def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose a "contested" resource where we are advantaged; break ties toward safer approach angles.
    best = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Strongly prefer resources we can reach strictly earlier; if equal, prefer those farther from opponent.
        lead = opd - myd
        key = (
            0 if myd < opd else 1,          # prefer earlier capture
            -lead,                          # larger lead better
            myd,                            # then closer
            -opd,                           # then farther for opponent
            rx, ry
        )
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Evaluate candidate moves by progress to target, avoiding obstacles, and denying opponent if we move adjacent to contested targets.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_next = man(nx, ny, tx, ty)
        my_now = man(sx, sy, tx, ty)
        progress = my_now - my_next

        # If our move brings us onto/near any contested resource we could steal next, prioritize it.
        steal = 0
        if progress >= 0:
            for rx, ry in resources:
                if (rx, ry) == (tx, ty):
                    continue
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                if myd <= opd and myd <= 2:
                    steal += (2 - myd) + (1 if myd < opd else 0)

        # Safety: slight penalty for moving away from global target.
        dist_pen = my_next

        # Opponent pressure: discourage moves that let opponent immediately reach the chosen target (one-step steal threat).
        oppd_next = man(ox, oy, tx, ty)
        threat = 1 if oppd_next <= my_next else 0

        val = (threat, -steal, -progress, dist_pen, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]