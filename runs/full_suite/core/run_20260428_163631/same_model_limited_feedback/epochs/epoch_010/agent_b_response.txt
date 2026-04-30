def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    # Choose best target: prefer resources closer than opponent and closer overall.
    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist2((sx, sy), (rx, ry))
        do = dist2((ox, oy), (rx, ry))
        # Larger is better; deterministic tie-break by coords.
        score = (do - ds) * 100 - ds
        key = (score, -rx, -ry, ds, do, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1] if best else (sx, sy)

    # Determine move delta toward target, avoiding obstacles.
    dx0 = 0 if tx == sx else (1 if tx > sx else -1)
    dy0 = 0 if ty == sy else (1 if ty > sy else -1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Priority: primary direction, then others by distance to target, then lexicographic.
    def move_key(m):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return (-10**18, 0)
        if (nx, ny) in obstacles:
            return (-10**18, 0)
        return (-dist2((nx, ny), (tx, ty)), 0)  # larger is better

    primary = (dx0, dy0)
    if primary in moves:
        if 0 <= sx + dx0 < w and 0 <= sy + dy0 < h and (sx + dx0, sy + dy0) not in obstacles:
            return [dx0, dy0]

    bestm = None
    for m in sorted(moves):
        k = move_key(m)
        if k[0] < -10**17:
            continue
        if bestm is None or k > bestm[0]:
            bestm = (k, m)
    if bestm is None:
        return [0, 0]
    return [bestm[1][0], bestm[1][1]]