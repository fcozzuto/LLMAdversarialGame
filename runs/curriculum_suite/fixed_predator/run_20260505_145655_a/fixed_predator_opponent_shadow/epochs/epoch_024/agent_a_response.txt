def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    best_t = None
    best_tv = None
    for rx, ry in resources:
        d_me = man((rx, ry), (x, y))
        d_opp = man((rx, ry), (ox, oy))
        # Prefer cells where we can outpace opponent; tie-break toward closer overall.
        tv = (d_opp - d_me) * 200 - d_me + (abs(ox - rx) + abs(oy - ry)) * 0.01
        if best_tv is None or tv > best_tv:
            best_tv, best_t = tv, (rx, ry)

    tx, ty = best_t
    best_move = (0, 0)
    best_mv = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        if nx == x and ny == y:
            step_pen = 1
        else:
            step_pen = 0
        d_me = abs(tx - nx) + abs(ty - ny)
        d_opp = abs(tx - ox) + abs(ty - oy)
        # Move to reduce our time-to-target and keep advantage over opponent.
        mv = (d_opp - d_me) * 200 - d_me - step_pen
        # Small bias to avoid drifting toward opponent after taking resource path.
        mv -= (man((nx, ny), (ox, oy)) * 0.02)
        if best_mv is None or mv > best_mv:
            best_mv, best_move = mv, (dx, dy)

    if best_mv is None:
        # All candidate moves blocked (rare); deterministic fallback.
        dx = -sign(tx - x)
        dy = -sign(ty - y)
        if inb(x + dx, y + dy) and not blocked(x + dx, y + dy):
            return [dx, dy]
        return [0, 0]

    return [best_move[0], best_move[1]]