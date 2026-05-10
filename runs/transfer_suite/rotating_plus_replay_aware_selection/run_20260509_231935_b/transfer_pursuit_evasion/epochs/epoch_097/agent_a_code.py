def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    sr = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in sr) or ("pursue" in sr)

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    pref = [(0,0), (1,1), (-1,-1), (1,-1), (-1,1), (1,0), (-1,0), (0,1), (0,-1)]
    order = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    def dist(x, y):
        dx = x - ox
        dy = y - oy
        return abs(dx) + abs(dy)

    def free_neighbors(x, y):
        c = 0
        for a, b in moves:
            nx, ny = x + a, y + b
            if ok(nx, ny):
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny)
        fn = free_neighbors(nx, ny)
        # obstacle proximity penalty (soft)
        adj_obs = 0
        for a, b in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)]:
            if (nx+a, ny+b) in obs_set:
                adj_obs += 1
        # Score: pursuer wants smaller distance; evader wants larger distance.
        # Tie-break uses higher mobility and then fewer adjacent obstacles.
        if is_pursuer:
            val = (0, d, -fn, adj_obs)
        else:
            val = (0, -d, -fn, adj_obs)
        if best_val is None or val < best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        # All moves invalid: stay put
        return [0, 0]
    return [int(best[0]), int(best[1])]