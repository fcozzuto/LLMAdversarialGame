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

    res_set = set((r[0], r[1]) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    # Choose a target where we have advantage; if none, choose the resource that would most benefit us to deny.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = ds - do  # smaller is better (we are closer or tie)
        # Secondary tie-breakers: prefer closer for us, and prefer being far from opponent in absolute distance
        key = (adv, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # deterministic fallback: drift toward center
        tx, ty = w // 2, h // 2
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            k = (cheb(nx, ny, tx, ty), nx, ny)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None
    base_ds = cheb(sx, sy, tx, ty)
    base_do = cheb(ox, oy, tx, ty)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) in res_set:
            return [dx, dy]  # immediate collection
        ns_ds = cheb(nx, ny, tx, ty)
        # Prefer reducing our distance; also prefer increasing our relative advantage to opponent.
        # Deterministic ordering via (val, dx, dy).
        our_progress = base_ds - ns_ds  # higher is better
        rel_adv = (base_do - ns_ds)  # higher is better: opponent distance - our distance after move
        # If we cannot improve, choose move that keeps options: minimize ns_ds then maximize rel_adv.
        val = (-our_progress, -rel_adv, ns_ds, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]