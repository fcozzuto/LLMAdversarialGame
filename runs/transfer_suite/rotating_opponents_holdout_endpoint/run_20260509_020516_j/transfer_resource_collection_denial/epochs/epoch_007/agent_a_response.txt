def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid_resources = []
    for rx, ry in resources:
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            valid_resources.append((rx, ry))
    if not valid_resources:
        return [0, 0]

    # If a resource is already at our move, prioritize it.
    adjacent = []
    for rx, ry in valid_resources:
        if max(abs(rx - sx), abs(ry - sy)) <= 1:
            adjacent.append((rx, ry))
    if adjacent:
        # deterministically pick best adjacent resource by our arrival (same) then opponent distance larger.
        best = None
        for rx, ry in adjacent:
            myd = max(abs(rx - sx), abs(ry - sy))
            od = dist(ox, oy, rx, ry)
            key = (od, -rx, -ry, myd)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        rx, ry = best[1]
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        return [dx, dy]

    # For each move, evaluate the best resource we could "secure": maximize (opp_dist - our_dist)
    # and then minimize our distance to that secured resource. Break ties by heading consistency.
    best_move = None
    best_key = None
    for dx0, dy0 in deltas:
        nx, ny = sx + dx0, sy + dy0
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep us, but keep consistent evaluation
        best_for_move = None
        for rx, ry in valid_resources:
            dS = dist(nx, ny, rx, ry)
            dO = dist(ox, oy, rx, ry)
            sec = dO - dS
            # Prefer equal-secure resources that are closer to us.
            # Slightly prefer reducing opponent's distance too.
            key = (sec, -dS, -(dO - dS), -rx, -ry)
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        # Additional deterministic tie-break: prefer moves that reduce max coordinate distance toward the chosen best-by-sec resource.
        # Use a simple proxy direction toward currently most valuable resource (overall).
        proxy_rx, proxy_ry = valid_resources[0]
        proxy_best = None
        for rx, ry in valid_resources:
            dS = dist(sx, sy, rx, ry)
            dO = dist(ox, oy, rx, ry)
            sec = dO - dS
            k = (sec, -dS, -rx, -ry)
            if proxy_best is None or k > proxy_best:
                proxy_best = k
                proxy_rx, proxy_ry = rx, ry
        move_dir = -max(abs(proxy_rx - (sx + dx0)), abs(proxy_ry - (sy + dy0)))
        overall_key = (best_for_move, move_dir, -dx0, -dy0)
        if best_key is None or overall_key > best_key:
            best_key = overall_key
            best_move = (dx0, dy0)

    return [int(best_move[0]), int(best_move[1])]