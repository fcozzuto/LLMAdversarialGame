def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obst = set((x, y) for x, y in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst:
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    # Target selection: contest resources where we can be closer than opponent
    best = None
    for nx, ny, dx, dy in candidates:
        best_r_val = -10**9
        for r in resources:
            ds = dist((nx, ny), r)
            do = dist((ox, oy), r)
            # Prefer resources where we become/are closer, with small pull to reduce our distance
            val = (do - ds) * 100.0 - ds
            # Mild tie-break: prefer nearer to center to reduce bad paths
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= 0.01 * (abs(nx - cx) + abs(ny - cy))
            if val > best_r_val:
                best_r_val = val
        # Also prefer not stepping away from all resources
        fallback = -min(dist((nx, ny), r) for r in resources) if resources else 0
        score = best_r_val + 1.0 * fallback
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]