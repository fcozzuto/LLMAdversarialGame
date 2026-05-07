def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, cheb(ox, oy, tx, ty))
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources where we can arrive first (or tie with smaller ds), then nearer.
        # Key: maximize (do - ds), but use minimization via negative.
        key = (- (do - ds), ds, cheb(rx, ry, w - 1 if sx < w // 2 else 0, h - 1 if sy < h // 2 else 0))
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Greedy step to reduce distance to target while avoiding obstacles;
    # if blocked, consider alternatives that delay opponent pickup.
    best_move = None
    best_k = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        # Opponent pressure at this step
        d_opp = cheb(ox, oy, tx, ty)
        # Penalize moving away from target; reward improving margin (opp - self).
        k = (d_self, - (d_opp - d_self), cheb(nx, ny, tx, ty))
        if best_move is None or k < best_k:
            best_move = [dx, dy]
            best_k = k

    return best_move if best_move is not None else [0, 0]