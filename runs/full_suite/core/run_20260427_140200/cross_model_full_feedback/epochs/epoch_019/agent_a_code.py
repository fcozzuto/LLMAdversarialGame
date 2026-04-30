def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h
    def free(x, y): 
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource where we have a relative advantage
    # Score: prioritize positive (opp_dist - my_dist), then smaller my_dist, then farther from opponent.
    best_move = None
    best_key = None
    for dx, dy, nx, ny in candidates:
        my_to_opp = man((nx, ny), (ox, oy))
        if not resources:
            # No resources: drift to reduce distance to opponent (deny if resources spawn there)
            key = (0, -my_to_opp, 0, dx, dy)
            if best_key is None or key < best_key:
                best_key, best_move = key, (dx, dy)
            continue

        local_best_key = None
        for tx, ty in resources:
            myd = man((nx, ny), (tx, ty))
            opd = man((ox, oy), (tx, ty))
            advantage = opd - myd  # higher is better
            # Convert to ordering: we want max advantage -> min -advantage; smaller myd; larger distance from opponent
            key = (-advantage, myd, -my_to_opp, (tx - nx) * 0 + 0, dx, dy)
            if local_best_key is None or key < local_best_key:
                local_best_key = key
        if local_best_key is None:
            local_best_key = (0, man((nx, ny), (sx, sy)), -my_to_opp, dx, dy)
        # Tie-break between moves by the chosen resource key only
        if best_key is None or local_best_key < best_key:
            best_key, best_move = local_best_key, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]