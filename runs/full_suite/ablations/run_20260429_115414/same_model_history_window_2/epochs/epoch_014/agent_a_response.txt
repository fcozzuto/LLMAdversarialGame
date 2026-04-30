def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        if p and len(p) >= 2:
            blocked.add((p[0], p[1]))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in blocked

    legal_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    if not resources or observation.get("remaining_resource_count", len(resources)) <= 0:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal_moves:
            v = -man((nx, ny), (cx, cy)) - 0.1 * man((nx, ny), (ox, oy))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    for dx, dy, nx, ny in legal_moves:
        my_pos = (nx, ny)
        my_best = -10**18
        for r in resources:
            rpos = (r[0], r[1])
            myd = man(my_pos, rpos)
            opd = man((ox, oy), rpos)
            advantage = opd - myd  # positive if I'm closer than opponent
            v = 1200 * advantage - 3 * myd
            if v > my_best:
                my_best = v
        v = my_best - 0.05 * man(my_pos, (ox, oy))
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]