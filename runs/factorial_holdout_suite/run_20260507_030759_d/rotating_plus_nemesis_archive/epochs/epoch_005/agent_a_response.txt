def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx if dx >= 0 else -dx if dy < 0 else (-dx if dx < 0 else dx)  # unreachable, keep deterministic

    def cdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Target: pick a resource where we have the best arrival advantage; if all worse, still pick best compromise.
    best = None
    tr = observation.get("turns_remaining", 0)
    for tx, ty in resources:
        myd = cdist(sx, sy, tx, ty)
        opd = cdist(ox, oy, tx, ty)
        # Prefer resources we can reach no later than opponent; then fastest for us; then deterministic.
        key = (myd - opd, myd, tx + ty * 0.001, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    # Obstacle-aware local choice: among valid moves, minimize our distance to target and maximize opponent disadvantage.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            my_after = cdist(nx, ny, tx, ty)
            op_after = cdist(ox, oy, tx, ty)
            # Secondary: slightly prefer moves that reduce distance to the *best* future resources (lightly via nearest resource to neighbor)
            best_future = None
            for rx, ry in resources:
                d = cdist(nx, ny, rx, ry)
                if best_future is None or d < best_future:
                    best_future = d
            candidates.append((
                (my_after - op_after, my_after, -best_future, nx, ny),
                [dx, dy]
            ))
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]