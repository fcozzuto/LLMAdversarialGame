def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    res = set((p[0], p[1]) for p in resources_list)
    obs = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources_list:
        return [0, 0]

    # Immediate pickup if legal
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    best_move = [0, 0]
    best_val = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate position by best "win margin" resource after moving
        # margin = opponent_time - self_time (bigger => more likely we collect first)
        local_best = None
        local_best_dist = None
        for rx, ry in res:
            sd = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            margin = od - sd
            if local_best is None or margin > local_best or (margin == local_best and sd < local_best_dist):
                local_best = margin
                local_best_dist = sd

        # If all margins equal (or no resources), keep deterministic ordering via tie-break
        # Prefer larger margin, then closer, then deterministic direction order
        tie = (local_best, -local_best_dist)
        if best_val is None or tie > best_val:
            best_val = tie
            best_move = [dx, dy]

    return best_move