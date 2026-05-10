def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Greedy pursuit: move that minimizes squared distance while avoiding obstacles.
    best = None
    best_dist = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in obs:
                continue
            ddx = nx - ox
            ddy = ny - oy
            dist = ddx * ddx + ddy * ddy
            # Slight preference for not staying and for closer progress when tied.
            stay_pen = 0 if (dx == 0 and dy == 0) else -1
            key = (dist, 0 if (dx == 0 and dy == 0) else -1)
            if best is None or key < (best_dist, best[2]):
                best = (dx, dy, key[1])
                best_dist = dist

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]