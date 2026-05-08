def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))
    if not resources:
        return [0, 0]

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    best_move = (0, 0)
    best_val = None  # lexicographic max
    # Prefer moves that (1) create largest advantage on some contested resource,
    # (2) also keep us close to that target, (3) avoid getting blocked by obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose best resource for this move from our new position.
        local_best = None
        for rx, ry in resources:
            my_d = dist8(nx, ny, rx, ry)
            op_d = dist8(ox, oy, rx, ry)
            adv = op_d - my_d  # positive means we are closer than opponent
            # Deterministic tie-breakers using coordinates.
            key = (adv, -my_d, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key

        if local_best is None:
            continue

        # Main value for this move
        adv, neg_my_d, neg_rx, neg_ry = local_best

        # Secondary robustness: discourage stepping next to obstacles if we don't gain advantage.
        # Count how many obstacle cells around us (lower is better).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obst:
                    adj_obs += 1
        val = (adv, neg_my_d, -adj_obs, neg_rx, neg_ry)

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]