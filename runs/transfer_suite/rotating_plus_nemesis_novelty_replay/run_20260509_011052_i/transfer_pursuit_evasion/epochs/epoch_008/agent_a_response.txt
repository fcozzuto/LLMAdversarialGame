def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    r = observation.get("capture_radius", 0)
    role = str(observation.get("self_role", "pursuer")).lower()
    is_evader = "evader" in role

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        return abs(x - ox) if abs(x - ox) > abs(y - oy) else abs(y - oy)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs.sort(key=lambda d: (d[0], d[1]))  # deterministic

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        dist = cheb(nx, ny)
        cap = 1 if (r == 0 and nx == ox and ny == oy) else 0

        # Obstacle proximity penalty (prefer moves with more free neighboring cells)
        free_n = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                ax, ay = nx + tx, ny + ty
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) not in obstacles:
                    free_n += 1

        # Simple "zig-zag robustness": discourage oscillating between two closest directions
        # using a deterministic bias based on parity and direction.
        bias = (nx + ny) % 2

        if is_evader:
            score = dist * 10 + free_n + (bias if (dx != 0 or dy != 0) else 0)
            if cap:
                score -= 10000
            want_better = (best_score is None) or (score > best_score)
        else:
            score = (-dist * 10) - (9 - free_n) - bias
            if cap:
                score += 10000  # capture immediately
            want_better = (best_score is None) or (score > best_score)

        if want_better:
            best_score = score
            best_move = [dx, dy]

    return best_move