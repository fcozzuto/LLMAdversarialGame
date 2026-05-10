def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_val = -10**18

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def adj_obstacle(nx, ny):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in obs:
                    return 1
        return 0

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            nx, ny = x, y
        gain = 0
        if (nx, ny) in unclaimed:
            gain += 6
        if (nx, ny) in opp:
            gain += 2
        if dx == 0 and dy == 0:
            gain -= 1
        dcenter = abs(nx - cx) + abs(ny - cy)
        val = gain + (-0.15 * dcenter) + (-2.0 * adj_obstacle(nx, ny))
        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]