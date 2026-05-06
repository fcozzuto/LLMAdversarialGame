def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target():
        if not resources:
            return (ox, oy)  # no resources: head toward opponent
        best = None
        best_sc = -10**18
        for rx, ry in resources:
            myd = cd(x, y, rx, ry)
            opd = cd(ox, oy, rx, ry)
            # Prefer resources I can reach before opponent, but keep pressure on contested ones
            sc = 12 * (opd - myd) - myd
            if sc > best_sc:
                best_sc = sc
                best = (rx, ry)
        return best

    tx, ty = best_target()

    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = x + dxm, y + dym
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = cd(nx, ny, tx, ty)
        opd = cd(ox, oy, tx, ty)
        # If we are closer than opponent to the same target, get bonus; also avoid giving them a fast route
        give_opd = cd(ox, oy, nx, ny)
        val = 14 * (opd - myd) - myd - 2 * give_opd
        # Small deterministic bias toward reducing both coords (tie-breaker)
        val -= 0.001 * (abs(nx - tx) + abs(ny - ty))
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]