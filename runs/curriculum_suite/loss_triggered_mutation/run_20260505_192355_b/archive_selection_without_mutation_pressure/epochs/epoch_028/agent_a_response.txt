def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        center_pen = abs(nx - cx) + abs(ny - cy)
        # Evaluate move by the best resource opportunity it creates vs opponent.
        local_best = None
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            adv = opd - myd  # positive: we're closer
            edge_pen = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)  # prefer larger (more interior)
            # Combine: strongly prefer being closer, then prefer nearer, then interior control.
            val = (adv * 6.0) - (myd * 1.2) - (center_pen * 0.15) + (edge_pen * 0.08)
            if local_best is None or val > local_best:
                local_best = val
        if local_best is None:
            continue
        # Tie-break deterministically by preferring (0,0) then lexicographic move.
        tiebreak = (0 if (dx, dy) == (0, 0) else 1, dx, dy)
        score_tuple = (local_best, -tiebreak[0], -tiebreak[1], -tiebreak[2])
        if best_score is None or score_tuple > best_score:
            best_score = score_tuple
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]