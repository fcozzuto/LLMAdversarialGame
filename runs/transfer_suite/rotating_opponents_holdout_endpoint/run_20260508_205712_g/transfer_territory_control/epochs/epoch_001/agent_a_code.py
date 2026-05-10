def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    unclaimed = observation.get("unclaimed_cells", []) or []

    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if unclaimed:
        target = min(unclaimed, key=lambda p: dist((sx, sy), p))
        best = None
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            d_to = dist((nx, ny), target)
            d_opp = dist((nx, ny), (ox, oy))
            score = -d_to + 0.01 * d_opp
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    cx, cy = w // 2, h // 2
    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_center = dist((nx, ny), (cx, cy))
        d_opp = dist((nx, ny), (ox, oy))
        score = 0.02 * d_opp - d_center
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]] if best is not None else [0, 0]