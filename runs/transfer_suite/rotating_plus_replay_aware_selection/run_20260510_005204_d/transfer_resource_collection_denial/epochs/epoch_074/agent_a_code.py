def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Pick target resource where we are relatively farther than opponent (opportunity to snatch)
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources opponent can reach no faster, but we can improve that situation with movement
        key = (opd - myd, -myd, -opd, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # If we are already on a resource, stay (deterministic)
    if (sx, sy) in set(tuple(p) for p in resources):
        return [0, 0]

    target_set = set(tuple(p) for p in resources)

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Secondary: if we can land on any resource, prioritize it strongly
        on_any = (nx, ny) in target_set

        # Also slightly prefer moves that increase our distance from opponent (reduce their future capture chance)
        opp_to_nearest = 10**9
        for rx, ry in resources:
            d = cheb(ox, oy, rx, ry)
            if d < opp_to_nearest:
                opp_to_nearest = d

        key = (
            (opd2 - myd2) + (3 if on_any else 0),
            -myd2,
            -(cheb(nx, ny, ox, oy)),
            (opp_to_nearest),
            rx if (rx := tx) is not None else 0,  # deterministic tie helper
            ry if (ry := ty) is not None else 0
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]