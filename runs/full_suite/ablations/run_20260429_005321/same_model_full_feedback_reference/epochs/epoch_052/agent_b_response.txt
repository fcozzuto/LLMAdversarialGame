def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # Small deterministic tie-break: prefer moves with lexicographically smallest delta among equals.
    best_move = (0, 0)
    best_val = -10**18

    # If no resources, head to center-ish deterministically.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = -d2(nx, ny, tx, ty)
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Evaluate each move by best "steal" opportunity among all resources.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        my_pos_dist_to_best = 10**18
        steal_val = -10**18

        for rx, ry in resources:
            md = d2(nx, ny, rx, ry)
            od = d2(ox, oy, rx, ry)

            # Prefer resources where we are closer than opponent (od - md),
            # with a small penalty for our distance and a slight bonus if it is actually nearest for us.
            val = (od - md) - (0.12 * md)
            if val > steal_val:
                steal_val = val
                my_pos_dist_to_best = md

        # Add a small "safety" term: avoid moves that get adjacent to obstacles too often.
        # (Deterministic and cheap.)
        adj_obs = 0
        for ex in (-1, 0, 1):
            for ey in (-1, 0, 1):
                if ex == 0 and ey == 0:
                    continue
                if (nx + ex, ny + ey) in obstacles:
                    adj_obs += 1

        # Prefer slightly lower adjacency and slightly smaller distance to selected resource.
        val_total = steal_val - (0.15 * my_pos_dist_to_best) - (0.6 * adj_obs)

        if val_total > best_val or (val_total == best_val and (dx, dy) < best_move):
            best_val = val_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]