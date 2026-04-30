def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources: keep pressure on the opponent side of the board.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if (ox + oy) > (sx + sy):
            tx, ty = 1 + (w - 2) // 2, 1 + (h - 2) // 2
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -(dist((nx, ny), (tx, ty)))
            # mild obstacle avoidance: prefer moves with more free adjacent cells
            free = 0
            for adx, ady in dirs:
                xx, yy = nx + adx, ny + ady
                if valid(xx, yy):
                    free += 1
            v += 0.05 * free
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Main objective: pick move that makes us closest to at least one resource
        # relative to opponent (op_dist - our_dist).
        rel_best = -10**9
        tie_res = None
        for r in resources:
            ourd = dist((nx, ny), r)
            opd = dist((ox, oy), r)
            rel = opd - ourd
            if rel > rel_best or (rel == rel_best and (tie_res is None or r < tie_res)):
                rel_best, tie_res = rel, r

        # Secondary: once relative advantage is good, also reduce our distance to that target.
        our_to_t = dist((nx, ny), tie_res) if tie_res is not None else 0

        free = 0
        for adx, ady in dirs:
            xx, yy = nx + adx, ny + ady
            if valid(xx, yy):
                free += 1

        val = 1000 * rel_best - our_to_t + 0.05 * free
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best_move = val, (dx, dy)

    return [best_move[0], best_move[1]]