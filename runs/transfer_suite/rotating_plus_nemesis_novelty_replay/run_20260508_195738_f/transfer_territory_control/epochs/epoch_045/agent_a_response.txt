def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    order = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    # Deterministic slight bias to vary behavior
    ti = int(observation.get("turn_index", 0))
    if ti % 2 == 1:
        order = order[4:] + order[:4]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def neigh_set(nx, ny):
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if inb(ax, ay):
                    yield ax, ay

    def score_cell(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        if (nx, ny) in opp:
            # Immediate flip is strong
            return 2000 + (5 if any((ax, ay) in selft for ax, ay in neigh_set(nx, ny)) else 0)
        if (nx, ny) in unclaimed:
            # Prefer expansion that also pressures opponent or connects to us
            neigh_op = any((ax, ay) in opp for ax, ay in neigh_set(nx, ny))
            neigh_us = any((ax, ay) in selft for ax, ay in neigh_set(nx, ny))
            return 900 + (220 if neigh_op else 0) + (160 if neigh_us else 0)
        if (nx, ny) in selft:
            # Keep within our blob; small preference toward opponent neighborhood
            neigh_op = any((ax, ay) in opp for ax, ay in neigh_set(nx, ny))
            return 20 + (80 if neigh_op else 0)
        # Other cells (should be rare): avoid
        return -50

    best_val = -10**18
    best_move = (0, 0)
    for i in order:
        dx, dy = dirs[i]
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = score_cell(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]