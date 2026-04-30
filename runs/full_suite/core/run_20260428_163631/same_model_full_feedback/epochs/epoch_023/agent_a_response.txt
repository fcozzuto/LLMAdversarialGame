def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        # Choose a contest target: prefer resources where (our dist - opponent dist) is small.
        # Also slightly prefer resources aligned toward our corner diagonal sweep.
        best_t = resources[0]
        best_score = 10**9
        for rx, ry in resources:
            d1 = abs(sx - rx) + abs(sy - ry)
            d2 = abs(ox - rx) + abs(oy - ry)
            sweep_bias = abs((rx - (w - 1 - sx))) + abs((ry - (h - 1 - sy)))
            score = (d1 - 0.85 * d2) + 0.02 * sweep_bias + 0.01 * (rx + ry)
            if score < best_score:
                best_score = score
                best_t = (rx, ry)
        tx, ty = best_t

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_d = abs(nx - tx) + abs(ny - ty)
        opp_d = abs(nx - ox) + abs(ny - oy)
        # Aggressive contest: get closer to target, keep distance from opponent, avoid tight proximity.
        val = 0.0
        val += -1.5 * our_d
        val += 0.9 * opp_d
        if resources:
            # Encourage stepping onto or adjacent to a resource.
            for rx, ry in resources:
                if (rx, ry) == (nx, ny):
                    val += 50
                elif abs(nx - rx) + abs(ny - ry) == 1:
                    val += 2
        # Discourage moving away from board/into dead-ends by penalizing low mobility.
        mob = 0
        for adx, ady in dirs:
            if ok(nx + adx, ny + ady):
                mob += 1
        val += 0.15 * mob
        # Deterministic tie-break: lexicographic on dx,dy favoring diagonals toward target.
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]