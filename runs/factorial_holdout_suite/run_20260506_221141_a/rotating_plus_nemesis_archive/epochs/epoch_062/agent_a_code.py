def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                if (x, y) not in obstacles:
                    resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    def step_towards(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return x + dx, y + dy

    def path_block_penalty(tx, ty):
        x, y = sx, sy
        pen = 0
        for _ in range(2):
            x, y = step_towards(x, y, tx, ty)
            if (x, y) in obstacles:
                pen += 2
                break
        return pen

    # Choose target: maximize relative advantage + obstacle-robustness.
    best_r = None
    best_score = None
    for rx, ry in resources:
        my_d = cheb((sx, sy), (rx, ry))
        op_d = cheb((ox, oy), (rx, ry))
        lead = op_d - my_d
        total = my_d + op_d
        score = lead * 20 - total - path_block_penalty(rx, ry)
        if best_score is None or score > best_score or (score == best_score and (rx < best_r[0] or (rx == best_r[0] and ry < best_r[1]))):
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r

    # Pick next move: avoid obstacles, maximize immediate lead, minimize distance to target.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        my_d2 = cheb((nx, ny), (tx, ty))
        op_d2 = cheb((ox, oy), (tx, ty))
        lead2 = op_d2 - my_d2
        # Prefer: higher lead2, then smaller my_d2, then smaller distance to our opposite corner (keeps consistency).
        corner_d = cheb((nx, ny), (w - 1, h - 1))
        key = (lead2, -my_d2, -corner_d)
        if best_tuple is None or key > best_tuple:
            best_tuple = key
            best_m = [dx, dy]

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]