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
            if best is None or k < best:
                best = k
        return [best[2] - sx, best[3] - sy] if best else [0, 0]

    # Choose resource with maximum reach advantage over opponent.
    best_rx = best_ry = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer or equal compared to opponent
        key = (-adv, ds, rx, ry)  # maximize adv, then minimize our distance, then deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    # Move greedily to improve advantage; if blocked, pick best alternative.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        adv = no - ns
        # Prefer higher advantage, then closer to target; tie-break by (nx,ny)
        key = (-adv, ns, nx, ny)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move else [0, 0]