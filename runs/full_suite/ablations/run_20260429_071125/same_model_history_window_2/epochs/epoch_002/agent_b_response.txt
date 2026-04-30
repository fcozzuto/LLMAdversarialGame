def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # chase opponent deterministically
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man((nx, ny), (ox, oy))
            key = (d, 0, dx, dy)
            if key < best:
                best = key
        return [int(best[2]), int(best[3])]

    # precompute resource positions
    res = [(r[0], r[1]) for r in resources]

    best_key = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        ds_min = 10**9
        do_min = 10**9
        for rx, ry in res:
            d_s = abs(rx - nx) + abs(ry - ny)
            if d_s < ds_min:
                ds_min = d_s
            d_o = abs(rx - ox) + abs(ry - oy)
            if d_o < do_min:
                do_min = d_o

        # Prefer being close to some resource, and being closer than opponent by margin.
        # Larger (do_min - ds_min) is better; we minimize negative margin.
        margin = do_min - ds_min
        key = (ds_min, -margin, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]