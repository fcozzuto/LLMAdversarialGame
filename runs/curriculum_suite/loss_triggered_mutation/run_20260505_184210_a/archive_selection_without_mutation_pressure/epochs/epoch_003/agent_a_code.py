def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w, h = observation["grid_width"], observation["grid_height"]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dso = man((sx, sy), (ox, oy))

    # If very close, prioritize contesting the opponent's vicinity.
    if dso <= 2:
        best = None
        bestk = None
        for dx, dy, nx, ny in legal:
            k = (man((nx, ny), (ox, oy)), -(nx - sx), -(ny - sy), dx, dy)
            if bestk is None or k < bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    # Otherwise, go for a resource that we can reach efficiently and that is not favored by the opponent.
    best_move = None
    best_k = None
    for dx, dy, nx, ny in legal:
        # Evaluate the best resource from this candidate move.
        local_best = None
        local_best_k = None
        for rx, ry in resources:
            myd = man((nx, ny), (rx, ry))
            opd = man((ox, oy), (rx, ry))
            if myd == 0:
                # immediate pickup is best
                k = (-10**9, -opd, 0, rx, ry)
            else:
                # Prefer: (1) low myd, (2) high opd-myd (opponent slower),
                # (3) being closer to a resource that stays farther from opponent next.
                k = (myd, -(opd - myd), man((nx, ny), (ox, oy)), rx, ry)
            if local_best_k is None or k < local_best_k:
                local_best_k = k
                local_best = (rx, ry)
        # Break ties to keep motion decisive but deterministic.
        final_k = (local_best_k, man((nx, ny), (ox, oy)), -nx, -ny, dx, dy)
        if best_k is None or final_k < best_k:
            best_k = final_k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]