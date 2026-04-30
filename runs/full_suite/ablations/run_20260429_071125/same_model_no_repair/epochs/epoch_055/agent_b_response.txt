def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Choose target with maximum advantage: (opponent_dist - my_dist), then prefer smaller my_dist, then stable tie-break.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (opd - myd, -myd, -(rx + 8 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    # Move that improves advantage for the chosen target; small secondary preference toward target.
    best = None
    best_mkey = None
    for dx, dy, nx, ny in legal:
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Prefer breaking deadlocks: if can't improve, still minimize myd2 and avoid approaching opponent's best pick too much.
        k1 = (opd2 - myd2, -myd2)
        # Additional deterministic nudge: prefer moving that decreases distance to any resource we are closer to than opponent.
        bonus = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if cheb(nx, ny, rx, ry) <= cheb(ox, oy, rx, ry):
                bonus += 1
        mkey = (k1[0], k1[1], bonus, -(nx + 8 * ny), dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best = (dx, dy)
    return [best[0], best[1]]