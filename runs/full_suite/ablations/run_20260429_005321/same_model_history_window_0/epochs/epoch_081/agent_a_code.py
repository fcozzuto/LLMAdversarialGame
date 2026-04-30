def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    nexts = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h: 
            continue
        if (nx, ny) in obstacles:
            continue
        nexts.append((dx, dy, nx, ny))
    if not nexts:
        return [0, 0]

    def manhattan(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    if not resources:
        # No visible resources: move toward center while keeping away from opponent
        center = (w//2, h//2)
        best = None
        for dx, dy, nx, ny in nexts:
            dopp = manhattan((nx, ny), (ox, oy))
            dcen = manhattan((nx, ny), center)
            key = (dopp, -dcen)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose move that makes us closest to a resource relative to opponent
    best_key = None
    best_move = (0, 0)
    # Precompute resources list as tuples
    res = [tuple(p) for p in resources]
    for dx, dy, nx, ny in nexts:
        my_next = (nx, ny)
        # Use the most favorable resource for us (max advantage)
        best_adv = None
        best_myd = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            myd = abs(rx - nx) + abs(ry - ny)
            opd = abs(rx - ox) + abs(ry - oy)
            # Advantage: positive if we are closer than opponent; add slight tie-break for speed
            adv = (opd - myd) * 10 - myd
            if best_adv is None or adv > best_adv or (adv == best_adv and myd < best_myd):
                best_adv = adv
                best_myd = myd
        # If somehow all resources blocked, fallback
        if best_adv is None:
            best_adv = -10**9
            best_myd = manhattan(my_next, res[0])
        # Also avoid getting too close to opponent (to reduce being contested)
        oppd_after = manhattan(my_next, (ox, oy))
        key = (best_adv, oppd_after, -best_myd, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]