def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    res_set = set((x, y) for x, y in resources)
    blocked = set((x, y) for x, y in obstacles)
    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    def d2(a, b):
        return (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])

    best_t = None
    best_key = None
    for r in resources:
        myd = d2((sx, sy), r)
        opd = d2((ox, oy), r)
        # Prefer winning races for resources; deterministic tie-break by coordinates
        key = (opd - myd, -myd, -r[1], -r[0])
        if best_key is None or key > best_key:
            best_key = key
            best_t = r

    tx, ty = best_t
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        myd = d2((nx, ny), (tx, ty))
        opd = d2((ox, oy), (tx, ty))
        score = (opd - myd)
        if (nx, ny) in res_set:
            score += 1000000
        # small bias to keep moving toward target
        score -= myd * 1e-6
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]