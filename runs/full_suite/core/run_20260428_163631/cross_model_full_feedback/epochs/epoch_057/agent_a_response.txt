def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If no resources, move to maximize distance from opponent.
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            v = man((nx, ny), (ox, oy))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose target resource with deterministic tie-breaking: closest, then lexicographic.
    best_t = None
    best_td = 10**18
    for rx, ry in resources:
        d = abs(rx - sx) + abs(ry - sy)
        if d < best_td or (d == best_td and (rx, ry) < best_t):
            best_td = d
            best_t = (rx, ry)
    tx, ty = best_t

    # Evaluate moves: progress toward target, avoid opponent, and lightly avoid being blocked.
    best = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        d_target_now = abs(nx - tx) + abs(ny - ty)
        d_target_next = abs(nx - tx) + abs(ny - ty)
        progress = (best_td - d_target_now)  # positive if closer to target
        d_opp = abs(nx - ox) + abs(ny - oy)
        # Strongly discourage adjacency to opponent; encourage keeping distance.
        opp_term = 0
        if d_opp <= 1:
            opp_term = -1000 - 100 * (1 - d_opp)
        else:
            opp_term = 10 * d_opp
        # Small penalty for moving into a "trap" with fewer future options.
        future_options = 0
        for ddx, ddy in deltas:
            fx, fy = nx + ddx, ny + ddy
            if inb(fx, fy) and (fx, fy) not in obstacles:
                future_options += 1
        trap_pen = -0.5 * (9 - future_options)

        # Deterministic tie-break: prefer lower dx, then dy.
        score = 50 * progress + opp_term - trap_pen - 0.01 * (d_target_next)
        key = (score, -nx, -ny, -dx, -dy)
        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]