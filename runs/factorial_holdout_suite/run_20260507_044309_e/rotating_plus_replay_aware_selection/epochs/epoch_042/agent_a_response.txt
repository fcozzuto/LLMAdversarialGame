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
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (ox + oy) else (0, 0)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            k = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), dx, dy)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Score resources by our advantage: opponent reach minus our reach.
    # Add tiny deterministic tiebreakers to reduce dithering.
    best_res = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # larger => we can get it sooner (or equally) than opponent
        # Prefer winning reach, then smaller ds, then smaller do, then position order.
        k = (-adv, ds, do, rx, ry)
        if best_key is None or k < best_key:
            best_key = k
            best_res = (rx, ry)

    rx, ry = best_res
    # One-step look: choose move that maximizes advantage after the move.
    best_move = None
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        # Estimate opponent pressure toward same target: assume opponent can respond in one step
        # by taking best possible reduction from current position.
        possible_do2 = cheb(ox, oy, rx, ry)
        # We use current opponent distance to keep deterministic and cheap.
        # Still favor our move that reduces ds2 and prevents opponent closeness.
        adv2 = possible_do2 - ds2
        k = (-adv2, ds2, cheb(ox, oy, rx, ry), dx, dy)
        if best_move_key is None or k < best_move_key:
            best_move_key = k
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]