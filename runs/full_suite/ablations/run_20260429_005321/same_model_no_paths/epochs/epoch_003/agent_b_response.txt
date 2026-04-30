def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def obstacle_pen(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        if (x+1, y) in obstacles: p += 1
        if (x-1, y) in obstacles: p += 1
        if (x, y+1) in obstacles: p += 1
        if (x, y-1) in obstacles: p += 1
        if (x+1, y+1) in obstacles: p += 1
        if (x+1, y-1) in obstacles: p += 1
        if (x-1, y+1) in obstacles: p += 1
        if (x-1, y-1) in obstacles: p += 1
        return p

    # pick target resource deterministically
    tx, ty = (w - 1) // 2, (h - 1) // 2
    if resources:
        best = None
        best_key = None
        for r in resources:
            rx, ry = r[0], r[1]
            myd = manh((sx, sy), (rx, ry))
            opd = manh((ox, oy), (rx, ry))
            adv = opd - myd  # positive means we're closer
            key = (-adv, myd, rx, ry)  # minimize negative adv => maximize adv, tie by closer and coords
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # choose move that maximizes immediate advantage toward target while avoiding obstacles
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = manh((nx, ny), (tx, ty))
        opd = manh((ox, oy), (tx, ty))
        adv = opd - myd
        val = (-(adv), myd, obstacle_pen(nx, ny), nx, ny)  # best is smallest
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]