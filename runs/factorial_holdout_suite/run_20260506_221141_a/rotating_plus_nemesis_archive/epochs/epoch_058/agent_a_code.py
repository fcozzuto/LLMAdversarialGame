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

    def mdist(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    # Pick a target that we can reach no later than opponent; bias away from opponent "sweep rows" by preferring same-row escape gaps.
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = mdist((sx, sy), (rx, ry))
        op_d = mdist((ox, oy), (rx, ry))
        lead = op_d - my_d  # larger => we are closer
        row_bias = -abs(ry - oy)  # prefer row far from opponent when opponent sweeps
        key = (lead, row_bias, -my_d, -(rx * 997 + ry))
        if best_key is None or key > best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best_m = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        my_d = mdist((nx, ny), (tx, ty))
        op_d = mdist((ox, oy), (tx, ty))
        # Also consider stealing: if we move onto a nearby resource we'd otherwise lose, prefer that.
        steal = 0
        for rx, ry in resources:
            if mdist((nx, ny), (rx, ry)) == 0:
                steal = 5
                break
        score = (op_d - my_d, -my_d, steal, -abs(ny - oy), -(dx * 3 + dy))
        if best_score is None or score > best_score:
            best_score, best_m = score, (dx, dy)

    return [int(best_m[0]), int(best_m[1])]