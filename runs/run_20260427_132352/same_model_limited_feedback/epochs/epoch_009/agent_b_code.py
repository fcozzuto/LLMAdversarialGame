def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for 8-dir

    # Pick a priority target resource we are relatively closer to
    target = None
    best_gap = -10**9
    best_d = 10**9
    for r in resources:
        rx, ry = r
        d_s = dist((sx, sy), (rx, ry))
        d_o = dist((ox, oy), (rx, ry))
        gap = d_o - d_s  # positive => we are closer
        if gap > best_gap or (gap == best_gap and d_s < best_d):
            best_gap = gap
            best_d = d_s
            target = (rx, ry)
    if target is None:
        # No resources: move away from opponent and prefer center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            val = dist((nx, ny), (ox, oy)) - 0.01 * max(abs(nx - cx), abs(ny - cy))
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    tx, ty = target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        # small pressure toward reducing opponent's access by keeping them farther from our chosen target
        d_o_t = dist((ox, oy), (tx, ty))
        val = (-100 * d_t) + (10 * d_o) - (0.5 * d_o_t)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]