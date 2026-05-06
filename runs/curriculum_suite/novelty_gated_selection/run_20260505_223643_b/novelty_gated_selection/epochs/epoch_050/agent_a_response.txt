def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    res_list = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_move = (0, 0)
    # Prefer a move that positions us to collect a resource while keeping the opponent at distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs_set:
            continue

        # Choose the best resource for this move under our safety/tempo objective.
        # Higher is better: closer resource (negative dist) and farther opponent (positive dist).
        best_val = None
        for rx, ry in res_list:
            rdist = man(nx, ny, rx, ry)
            odist = man(nx, ny, ox, oy)
            val = (-rdist) + (0.75 * odist)
            if best_val is None or val > best_val:
                best_val = val

        # Small deterministic bias toward movement to break ties without "behavior cloning".
        tie = (man(nx, ny, w - 1, h - 1), dx, dy)
        score = (best_val, -tie[0])
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]