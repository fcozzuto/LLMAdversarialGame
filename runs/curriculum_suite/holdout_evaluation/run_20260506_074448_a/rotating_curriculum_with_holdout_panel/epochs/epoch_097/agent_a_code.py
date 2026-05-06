def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def best_target_score(nx, ny):
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            return -dist2(nx, ny, tx, ty) - 0.25 * dist2(nx, ny, ox, oy)
        best_rel = -10**18
        best_my = 10**18
        for rx, ry in resources:
            myd = dist2(nx, ny, rx, ry)
            opd = dist2(ox, oy, rx, ry)
            rel = opd - myd  # prefer being closer to a resource than opponent is
            if rel > best_rel or (rel == best_rel and myd < best_my):
                best_rel = rel
                best_my = myd
        # progress and keep relative advantage more important than raw distance
        return best_rel * 4 - best_my + 0.01 * (dist2(nx, ny, ox, oy))

    best_move = [0, 0]
    best_sc = None
    # Deterministic tie-break: fixed move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = best_target_score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]
        elif sc == best_sc:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move