def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = observation.get("unclaimed_cells", []) or []
    opp_terr = observation.get("opponent_territory", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def score_cell(x, y):
        # Prefer unclaimed near center and nearer to us than opponent; also mildly avoid opponent proximity.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        d_us = abs(x - sx) + abs(y - sy)
        d_op = abs(x - ox) + abs(y - oy)
        center = abs(x - cx) + abs(y - cy)
        opp_close = abs(x - ox) <= 1 and abs(y - oy) <= 1
        return (d_op - d_us, center, 0 if not opp_close else 1)

    best_t = None
    best_k = None
    for (tx, ty) in unclaimed:
        if free(tx, ty):
            k = score_cell(tx, ty)
            if best_k is None or k < best_k:
                best_k, best_t = k, (tx, ty)

    # If no unclaimed target, push into opponent territory (closest that is reachable without stepping onto obstacle).
    if best_t is None and opp_terr:
        for (tx, ty) in opp_terr:
            if free(tx, ty):
                k = (abs(tx - sx) + abs(ty - sy) - (abs(tx - ox) + abs(ty - oy)) * 0.5,
                     abs(tx - (w - 1) / 2.0) + abs(ty - (h - 1) / 2.0))
                if best_k is None or k < best_k:
                    best_k, best_t = k, (tx, ty)

    # If still none, just move toward center.
    if best_t is None:
        tx, ty = int((w - 1) / 2.0), int((h - 1) / 2.0)
    else:
        tx, ty = best_t

    # Choose one-step move that minimizes distance to target while avoiding obstacles.
    best_m = [0, 0]
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # Tie-break: prefer moves that reduce opponent distance slightly (deterministic)
        d2 = abs(nx - ox) + abs(ny - oy)
        k = (d, d2, dx, dy)
        if best_d is None or k < best_d:
            best_d = k
            best_m = [dx, dy]
    return best_m