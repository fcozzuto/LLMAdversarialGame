def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # deterministic fallback: drift toward center
        cx, cy = w // 2, h // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    cx, cy = w // 2, h // 2
    best_r = None
    best_key = None
    # Choose target resource where we are more likely to arrive first
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        myd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        win = oppd - myd  # positive means we are closer (or equal with tie-break below)
        center = cheb(rx, ry, cx, cy)
        key = (win, -myd, -center, -(rx * 9 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        oppd2 = cheb(ox, oy, tx, ty)
        win2 = oppd2 - myd2

        # If we move onto a resource square (likely), strongly prefer it
        on_res = 1 if (nx, ny) in set((r[0], r[1]) for r in resources if len(r) >= 2) else 0

        # Prefer getting closer to target and slightly away from opponent
        dist_opp = cheb(nx, ny, ox, oy)
        target_dist = cheb(nx, ny, tx, ty)

        # Tie-break deterministically
        key = (win2, on_res, -target_dist, dist_opp, -(dx * dx + dy * dy), (nx, ny))
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]