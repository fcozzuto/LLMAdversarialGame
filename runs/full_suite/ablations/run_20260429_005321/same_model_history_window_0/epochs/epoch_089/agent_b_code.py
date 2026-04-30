def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    myx, myy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] if observation["resources"] else []
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = myx + dx, myy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if (nx, ny) == (ox, oy):
            # still allowed by engine, but treat as risky/neutral
            pass
        # Choose the resource that best benefits us from this move
        best = -10**9
        if resources:
            for rx, ry in resources:
                myd = abs(nx - rx) + abs(ny - ry)
                opd = abs(ox - rx) + abs(oy - ry)
                # Prefer being much closer than opponent; also slightly prefer nearer resources and central moves
                center_pen = 0.05 * (abs(nx - cx) + abs(ny - cy))
                score = (opd - myd) * 1.2 - 0.08 * myd - center_pen
                if score > best:
                    best = score
        else:
            # If no resources, move to center while not walking into obstacles
            best = -0.1 * (abs(nx - cx) + abs(ny - cy)) + 0.0
        # Deterministic tie-break: prefer moves that keep us closer to opponent's position less (intercept), then lexicographic
        inter = -0.03 * (abs(nx - ox) + abs(ny - oy))
        candidates.append((-(best + inter), dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort()
    return [candidates[0][1], candidates[0][2]]