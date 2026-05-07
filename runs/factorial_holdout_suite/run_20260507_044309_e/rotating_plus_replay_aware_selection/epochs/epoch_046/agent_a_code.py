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
            k = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), nx, ny)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose resource where we have the greatest "reach advantage" vs opponent.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer or equal (with our distance smaller)
        k = (-adv, ds, rx, ry)  # maximize adv; then smaller ds; then deterministic
        if best_key is None or k < best_key:
            best_key = k
            best_res = (rx, ry)

    tx, ty = best_res

    # Move to minimize our distance to target; ties favor moving to a cell that
    # keeps the opponent relatively farther (static heuristic) and deterministic ordering.
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(ox, oy, tx, ty)
        # Prefer closer; then prefer larger opponent distance; then deterministic.
        score = (dself, -dop, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_move else [0, 0]