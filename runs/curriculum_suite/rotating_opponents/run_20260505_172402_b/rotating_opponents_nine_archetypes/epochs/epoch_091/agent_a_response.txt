def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for y in range(h):
            for x in range(w):
                if valid(x, y):
                    sx, sy = x, y
                    break
            if valid(sx, sy):
                break

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            x, y = sx + dx, sy + dy
            if valid(x, y):
                moves.append((dx, dy))

    if not resources:
        # No resources: drift to maximize distance from opponent.
        best = None
        bestd = None
        for dx, dy in moves:
            x, y = sx + dx, sy + dy
            d = abs(x - ox) + abs(y - oy)
            if best is None or d > bestd or (d == bestd and (dx, dy) < best):
                best, bestd = (dx, dy), d
        return list(best if best is not None else (0, 0))

    # Evaluate each move: choose one that best progresses toward a resource while staying relatively far from opponent.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        opp_d = abs(nx - ox) + abs(ny - oy)
        # Greedy over resources using a self-progress vs opponent-blocking balance.
        val = None
        for rx, ry in resources:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            # Prefer lower self distance and higher relative advantage over opponent.
            score = sd - 0.9 * (od - opp_d * 0.02)
            if val is None or score < val:
                val = score
        # If equal, prefer larger opponent distance and then diagonal progress.
        diag = abs((nx - sx) - (ny - sy))
        composite = (val, -opp_d, diag)
        if best is None or composite < best_val:
            best = (dx, dy)
            best_val = composite

    return [best[0], best[1]] if best is not None else [0, 0]