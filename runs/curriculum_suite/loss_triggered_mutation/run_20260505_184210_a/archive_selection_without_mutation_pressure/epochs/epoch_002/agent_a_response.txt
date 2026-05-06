def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    dso = man((sx, sy), (ox, oy))
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if dso <= 2:
        best = None
        bestk = None
        for dx, dy, nx, ny in legal:
            k = (man((nx, ny), (ox, oy)), -(nx - sx), -(ny - sy), dx, dy)
            if bestk is None or k < bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    # Target a resource I'm likely to secure: prefer low my distance, then prefer it being farther from opponent.
    best_target = None
    best_tk = None
    for rx, ry in resources:
        myd = man((sx, sy), (rx, ry))
        opd = man((ox, oy), (rx, ry))
        # second term rewards advantage (opd - myd); third term stable tie-break by coordinates
        tk = (myd, -(opd - myd), rx, ry)
        if best_tk is None or tk < best_tk:
            best_tk = tk
            best_target = (rx, ry)

    tx, ty = best_target

    # Greedy move toward target, with a meaningful anti-opponent term.
    # If the move would bring us closer to target while also moving away from opponent, prefer it.
    best = (0, 0)
    bestk = None
    for dx, dy, nx, ny in legal:
        myd_next = man((nx, ny), (tx, ty))
        od_next = man((nx, ny), (ox, oy))
        # Prefer smaller target distance; then prefer larger separation from opponent.
        k = (myd_next, -od_next, abs(dx) + abs(dy), dx, dy)
        if bestk is None or k < bestk:
            bestk = k
            best = (dx, dy)

    return [best[0], best[1]]