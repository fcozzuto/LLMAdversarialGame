def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    tr = observation.get("turns_remaining", 0)

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for (dx, dy) in moves if inside(sx + dx, sy + dy)]

    # Pick a target resource that we can win first (or at least contest) deterministically.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # urgency: prefer resources we can reach sooner; break ties by winning margin then distance
        key = (opd - myd, myd, rx, ry)
        # only prefer those we can likely reach within remaining time
        if tr and myd > tr + 1:
            key = (key[0] + 1000, key[1], key[2], key[3])
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if not best:
        return [0, 0]
    tx, ty = best

    # Move choice: greedily step toward target while reducing opponent advantage after the move.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # tie-breakers: maximize capture lead, then minimize distance to target, then deterministic ordering
        lead = opd2 - myd2  # smaller is better (we want negative => ahead)
        key = (lead, myd2, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]