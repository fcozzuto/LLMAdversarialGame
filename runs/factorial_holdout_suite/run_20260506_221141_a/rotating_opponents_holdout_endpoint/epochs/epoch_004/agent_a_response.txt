def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    if not resources:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a deterministic target: prefer where we are closer than opponent (advantage).
    best = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        adv = opd - myd  # + means we are closer
        key = (-adv, myd, opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in moves:
        moves.append((0, 0))

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        myd = dist(nx, ny, tx, ty)
        opd = dist(ox, oy, tx, ty)
        adv_after = opd - myd

        # If same advantage, prioritize moving closer; if still tied, reduce opponent's best denial pressure.
        den_best = 10**9
        for r2x, r2y in resources:
            den_best = min(den_best, dist(ox, oy, r2x, r2y))
        key = (
            -adv_after,
            myd,
            dist(nx, ny, ox, oy),
            den_best,
            nx,
            ny,
        )
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]