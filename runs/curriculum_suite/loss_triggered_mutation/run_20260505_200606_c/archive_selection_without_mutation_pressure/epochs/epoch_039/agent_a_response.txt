def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    parity = observation.get("turn_index", 0) & 1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by trying to deny the most "available" opponent resource while still improving our access.
        worst = 10**9
        total = 0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # If opponent is closer, we get higher priority to intercept; if we are closer, prefer fast collection.
            intercept_need = (do - ds)
            # Penalize moves that leave us far behind for the closest opponent-attempts.
            val_r = intercept_need * 120 - ds * 6 - do * (2 if parity == 0 else 3)
            total += val_r
            if intercept_need < 0:
                worst = min(worst, -intercept_need)

        # Combine: strong preference to maximize total, and avoid moves where we are consistently behind.
        consistency_pen = worst * (18 if parity == 0 else 12)
        score = total - consistency_pen

        # Deterministic tie-breaker: prefer moves that reduce distance to the single best resource for us.
        if score > best_val:
            best_val = score
            best_move = (dx, dy)
        elif score == best_val:
            tie_ds = min(man(nx, ny, rx, ry) for rx, ry in resources)
            best_nx, best_ny = sx + best_move[0], sy + best_move[1]
            best_ds = min(man(best_nx, best_ny, rx, ry) for rx, ry in resources)
            if tie_ds < best_ds:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]