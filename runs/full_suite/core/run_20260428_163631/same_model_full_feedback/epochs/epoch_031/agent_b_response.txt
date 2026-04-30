def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = resources if resources else [(w // 2, h // 2)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = None

    # Evaluate each immediate move by choosing the best target under an "interference" objective.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # If we have no resources, just head toward center.
        if targets:
            best_target_val = None
            for tx, ty in targets:
                my_d = cheb(nx, ny, tx, ty)
                op_d = cheb(ox, oy, tx, ty)
                # Prefer targets we reach faster than the opponent; slight bias toward closer resources.
                # Lower is better: (my_d) - 1.05*(op_d) + tiny tie-bias toward center distance.
                center_bias = cheb(nx, ny, w // 2, h // 2) * 0.02
                val = my_d - 1.05 * op_d + center_bias
                if best_target_val is None or val < best_target_val:
                    best_target_val = val

            cur_val = best_target_val
        else:
            cur_val = cheb(nx, ny, w // 2, h // 2)

        if best_val is None or cur_val < best_val:
            best_val = cur_val
            best = (dx, dy)
        elif cur_val == best_val:
            # Deterministic tie-break: prefer smaller dx, then smaller dy magnitude toward staying closer to current x/y.
            if abs(dx) < abs(best[0]) or (abs(dx) == abs(best[0]) and abs(dy) < abs(best[1])):
                best = (dx, dy)

    return [int(best[0]), int(best[1])]