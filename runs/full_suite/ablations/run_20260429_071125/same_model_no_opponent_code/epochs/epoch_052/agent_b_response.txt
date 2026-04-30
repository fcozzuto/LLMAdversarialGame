def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        ax -= bx; ay -= by
        return ax if ax > ay else ay if ay > ax else ax if ax == 0 else ay

    def min_dist_to_resources(nx, ny):
        if not resources:
            return 999
        best = 999
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_val = -10**18
    # Prefer moves that reduce resource distance; avoid getting too close to opponent (collision/steal).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_res = min_dist_to_resources(nx, ny)
        d_opp = abs(nx - ox) + abs(ny - oy)
        # Higher is better
        val = 0
        val += -2.0 * d_res
        val += 0.8 * d_opp
        # Strong deterrent if adjacent/very near to opponent
        if cheb((nx, ny), (ox, oy)) <= 1:
            val -= 10.0
        # Slight encouragement to move toward the center when resources are far
        if d_res >= 6:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= 0.15 * (abs(nx - cx) + abs(ny - cy))
        # Deterministic tie-breaker: fixed ordering already; keep first max
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]