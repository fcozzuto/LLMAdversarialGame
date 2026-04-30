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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    # Pick a target we are likely to reach first (or at least less badly than opponent).
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Lower is better; reward being closer than opponent.
        key = (myd - opd, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # If opponent is much closer to the chosen target, retarget to a resource that minimizes their advantage.
    myd0 = cheb(sx, sy, tx, ty)
    opd0 = cheb(ox, oy, tx, ty)
    if opd0 - myd0 >= 2:
        alt_key = None
        alt = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # minimize (opponent advantage - our progress); break ties by closeness to us
            k = (opd - myd, myd, rx, ry)
            if alt_key is None or k < alt_key:
                alt_key = k
                alt = (rx, ry)
        tx, ty = alt

    # Choose move that reduces our distance to the target while discouraging opponent progress.
    best_move = None
    best_val = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # primary: get closer
        # secondary: if opponent is closer, reduce their effective pressure by also increasing their distance to some nearby resource
        near_boost = 0
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if cheb(nx, ny, rx, ry) <= 1:
                near_boost += 1
        val = (myd, (opd - myd), -near_boost, abs((nx - tx)), abs((ny - ty)), rx if False else 0)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]