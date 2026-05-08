def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])[:2]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    ot = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_in_set(p, s):
        x, y = p
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in s:
                return True
        return False

    if not unclaimed and not ot:
        return [0, 0]

    # Pick a deterministic target: prioritize unclaimed cells adjacent to opponent, else opponent cells, else any unclaimed.
    frontier = []
    for c in unclaimed:
        if adj_in_set(c, ot):
            frontier.append(c)
    if frontier:
        candidates = frontier
    elif ot:
        candidates = list(ot)
    else:
        candidates = list(unclaimed)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for x, y in candidates:
        d = abs(x - sx) + abs(y - sy)
        center = abs(x - cx) + abs(y - cy)
        # Prefer frontier more strongly; if targeting opponent directly, slightly prefer direct adjacency.
        k_front = -1 if (x, y) in frontier else 0
        k_op = -2 if (x, y) in ot else 0
        key = (d + 0.08 * center, -(k_front + k_op), x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Choose move that best advances toward target, with strong bias to enter opponent territory.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        enter_op = (nx, ny) in ot
        to = abs(tx - nx) + abs(ty - ny)
        closeness_self = abs(tx - sx) + abs(ty - sy)
        improved = 0 if to >= closeness_self else -1
        step_front = -1 if ((nx, ny) in unclaimed and adj_in_set((nx, ny), ot)) else 0
        key = (0 if enter_op else 1, to, step_front + improved, nx, ny)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]