def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources") or []

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    deltas = (-1, 0, 1)
    legal = []
    for dx in deltas:
        for dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    free_res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not free_res:
        tx, ty = (w - 2 if w >= 2 else 0), (h - 2 if h >= 2 else 0)
        best = None
        best_move = (0, 0)
        for dx, dy, nx, ny in legal:
            key = (d(nx, ny, tx, ty), d(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best, best_move = key, (dx, dy)
        return [best_move[0], best_move[1]]

    # Opponent threat: resources they can reach in 1 move (or already adjacent/at).
    threatened = set()
    for dx in deltas:
        for dy in deltas:
            nx, ny = ox + dx, oy + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                for rx, ry in free_res:
                    if nx == rx and ny == ry:
                        threatened.add((rx, ry))
    # Deterministic choice: build a value for each candidate step.
    # Prefer: (1) quickest access to a "safe" resource, (2) denial of threatened resources
    # by moving to positions that increase their distance, (3) slight favor for approaching opponent
    # only if it also improves resource access.
    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        safe = [(rx, ry) for (rx, ry) in free_res if (rx, ry) not in threatened]
        target_list = safe if safe else free_res
        # Time to best target from this move
        best_t = None
        best_pos = None
        for rx, ry in target_list:
            tt = d(nx, ny, rx, ry)
            if best_t is None or tt < best_t or (tt == best_t and (rx, ry) < best_pos):
                best_t, best_pos = tt, (rx, ry)
        # Denial: how much farther we are from threatened resources than we are from opponent
        # (higher is better), and also how much we block their immediate capture routes.
        deny_min = 10**9
        for rx, ry in threatened:
            deny_min = min(deny_min, d(nx, ny, rx, ry))
        # Opponent distance: prefer moves that don't hand them a free capture path (reduce their proximity)
        opp_after = d(nx, ny, ox, oy)
        # Composite key (lexicographic): minimize time, maximize deny/opp threat, then deterministic tie-break.
        # Use negative terms where "larger is better".
        key = (
            best_t,
            -deny_min,
            opp_after,
            dx,
            dy,
            nx,
            ny,
        )
        if best_key is None or key < best_key:
            best_key, best_move = key, (dx, dy)

    return [best_move[0], best_move[1]]