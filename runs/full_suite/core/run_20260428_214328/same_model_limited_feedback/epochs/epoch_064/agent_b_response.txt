def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # If no resources visible, drift toward opponent's side while staying safe
    if not resources:
        tx = (w - 1) if sx < w // 2 else 0
        ty = (h - 1) if sy < h // 2 else 0
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -(abs(nx - tx) + abs(ny - ty)) - 0.1 * mdist((nx, ny), (ox, oy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Choose move that maximizes:
    # - closeness to best available resource
    # - winning probability on that resource (being closer than opponent)
    # - slight avoidance of getting too close to opponent
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_to = [(mdist((nx, ny), r), r) for r in resources]
        my_to.sort(key=lambda t: t[0])
        d1, r1 = my_to[0]
        opp_d1 = mdist((ox, oy), r1)
        # secondary tie-break: second-closest resource
        d2 = my_to[1][0] if len(my_to) > 1 else 999
        contest = (opp_d1 - d1)  # positive if we are closer
        v = (-10 * d1) + (3.0 * contest) + (-1.0 * d2) - 0.05 * mdist((nx, ny), (ox, oy))
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return [best[0], best[1]]