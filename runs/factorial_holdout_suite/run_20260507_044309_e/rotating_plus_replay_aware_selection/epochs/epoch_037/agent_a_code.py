def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            k = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), nx, ny)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Pick a resource with maximum "reach advantage" over opponent.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer positive advantage; then smaller own distance; then deterministic tie by coords.
        key = (ds - do, -ds, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target if best_target is not None else (w // 2, h // 2)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If multiple resources are close, bias toward reducing opponent access to the same nearest resource.
    next_target = None
    next_best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = cheb(ox, oy, rx, ry)
        key = (d, -rx, -ry)
        if next_best is None or key < next_best:
            next_best = key
            next_target = (rx, ry)

    if next_target is None:
        next_target = (tx, ty)

    best_move = None
    best_key2 = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do_new = cheb(ox, oy, tx, ty)
        # Primary: move to reduce own distance; Secondary: deny opponent (prefer moves that keep ds advantage).
        # Also add tiny deterministic tie-breaker favoring decreasing x then y.
        k = (ds_new - do_new, ds_new, cheb(nx, ny, next_target[0], next_target[1]), nx, ny)
        if best_key2 is None or k < best_key2:
            best_key2 = k
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]