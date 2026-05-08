def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target we can likely secure: prefer resources where we're ahead.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        ahead = do - ds  # positive if we're closer
        # If can't be ahead, still prefer smaller self distance.
        key = (-(ahead), ds)  # deterministically maximize ahead, then minimize ds
        if best is None or key < best[0]:
            best = (key, (rx, ry, ds, do))
    if best is None:
        return [0, 0]

    tx, ty, ds, do = best[1]
    if sx == tx and sy == ty:
        return [0, 0]

    # Greedy one-step move toward target with obstacle and "don't help opponent" considerations.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nds = dist(nx, ny, tx, ty)

        # Opponent counter: avoid moving into positions that reduce opponent's advantage too much.
        # Approximate by comparing our resulting distance vs opponent distance to the same target.
        nd_adv = (do - nds)  # larger is better for us
        # Also mildly favor reducing distance to the closest resource overall to avoid getting trapped.
        min_self_to_any = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dtemp = dist(nx, ny, rx, ry)
            if min_self_to_any is None or dtemp < min_self_to_any:
                min_self_to_any = dtemp
        if min_self_to_any is None:
            min_self_to_any = nds

        # Deterministic scoring: primary reduce target distance, secondary maximize being ahead, then global closeness.
        score = (nds, -nd_adv, min_self_to_any, dx, dy)
        if bestm is None or score < bestm[0]:
            bestm = (score, [dx, dy])

    if bestm is None:
        return [0, 0]
    return bestm[1]