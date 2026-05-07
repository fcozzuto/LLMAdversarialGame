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

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            k = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), nx, ny)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose target where we have reach advantage over opponent (minimize opponent-distance - self-distance),
    # and among those, prefer smaller self-distance; then deterministic tie-break by coordinates.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv_key = (do - ds, ds, rx, ry)  # smaller is better: higher advantage, then closer
        if best_key is None or adv_key < best_key:
            best_key = adv_key
            best_target = (rx, ry)

    tx, ty = best_target
    cx = 0 if tx == sx else (1 if tx > sx else -1)
    cy = 0 if ty == sy else (1 if ty > sy else -1)

    # If the direct step is blocked, try alternative steps that keep reducing self chebyshev distance to target.
    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)  # mild secondary: avoid moving toward opponent too much
        k = (ns, abs(do - ds), no, nx, ny)
        if best is None or k < best:
            best = k
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]