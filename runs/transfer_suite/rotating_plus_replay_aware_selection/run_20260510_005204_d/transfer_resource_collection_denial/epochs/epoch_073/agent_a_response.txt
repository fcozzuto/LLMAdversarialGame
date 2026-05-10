def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_key = None
    tx = ty = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach at least as fast, then those with larger opponent disadvantage.
        # Tie-break deterministically: prefer closer to us after advantage.
        key = (opd - myd, -myd, -cheb(rx, ry, 0, 0), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    # One-step lookahead with opponent-aware score:
    # Maximize (opp_distance_to_target - my_distance_to_target) after move,
    # and slightly prefer reducing our distance to target.
    best_move = (0, 0)
    best_score = None
    cur_my = cheb(sx, sy, tx, ty)
    cur_opd = cheb(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)  # opponent position doesn't change during our move
        # If we don't improve our advantage, still allow for progress toward target.
        # Add a small term to avoid ties that can stall near obstacles.
        score = (opd2 - myd2, -(myd2 + 0.1 * (myd2 - cur_my)), -cheb(nx, ny, tx, ty), -cheb(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]