def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If current position is blocked somehow, just move deterministically away.
    if (sx, sy) in blocked:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    # Deterministic resource selection:
    # 1) prefer resources we can reach earlier (margin positive),
    # 2) strongly avoid resources that opponent can reach much earlier,
    # 3) break ties by our distance then by coordinates.
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we arrive earlier
        if ds == 0:
            margin = 999  # immediate pickup
        # Penalize heavily if opponent has a clear advantage.
        # Also slightly penalize far targets to reduce wandering.
        adv_pen = 0
        if margin <= -1:
            adv_pen = (-margin) * (-margin) * 3
        tie = (-ds, -rx, -ry)
        key = (margin - adv_pen, tie[0], tie[1], tie[2])
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    if best is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best[1]

    # Choose move that decreases distance to target; keep deterministic tie-breaks.
    best_move = (None, None)  # (dist, score)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        d_to = cheb(nx, ny, tx, ty)
        # Also consider whether we are moving into the opponent's likely contention:
        # prefer steps that increase our advantage over opponent (local, still cheap).
        d_opp = cheb(ox, oy, tx, ty)
        my_future_margin = d_opp - d_to
        # score higher is better
        score = (my_future_margin, -d_to, -abs((nx - ox)) - abs((ny - oy)), -rx if False else 0)
        if best_move[0] is None or (d_to < best_move[0]) or (d_to == best_move[0] and score > best_move[1]):
            best_move = (d_to, score)
            best_delta = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [best_delta[0], best_delta[1]]