def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    viable = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in blocked]
    if viable:
        best = None
        best_key = None
        for rx, ry in viable:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            contest = od - myd  # positive if we are closer
            key = (-contest, myd, rx, ry)  # maximize contest, then minimize our distance, then deterministic tie-break
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx = w - 1 if sx < w - 1 else 0
        ty = h - 1 if sy < h - 1 else 0

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        my_to_opp = cheb(nx, ny, ox, oy)
        # Prefer moves that improve contest; if equal, prefer closer to target and farther from opponent.
        val = 100 * (od2 - myd2) - 10 * myd2 - my_to_opp
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_val is None:
        # If all moves blocked, stay.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]