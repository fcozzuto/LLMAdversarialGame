def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a likely denier target: where opponent is closer than we are.
    # If none, pick the resource where we're most behind.
    best_r = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        behind = myd - opd  # positive means we're farther (opponent likely wants it)
        if best_key is None:
            best_key = behind
            best_r = (rx, ry)
        else:
            # Prefer strongest opponent-advantage. If all bad, still prefer being most behind.
            if behind > best_key:
                best_key = behind
                best_r = (rx, ry)

    tx, ty = best_r

    # Move choice: contest target while not giving opponent an easy line to it.
    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to_t = cheb(nx, ny, tx, ty)
        op_to_t = cheb(ox, oy, tx, ty)

        # Secondary: prevent stepping towards any resource where opponent is closer (to avoid chasing their path).
        chase_pen = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            opd = cheb(ox, oy, rx, ry)
            myd2 = cheb(nx, ny, rx, ry)
            if opd < myd2:
                chase_pen += 1

        # Prefer larger (opponent distance - our distance), and reduce chase penalty.
        val = (op_to_t - my_to_t) * 10 - chase_pen

        # Tiny deterministic tie-break: prefer moves that reduce distance to target.
        if val > best_val or (val == best_val and my_to_t < cheb(sx, sy, tx, ty)):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]