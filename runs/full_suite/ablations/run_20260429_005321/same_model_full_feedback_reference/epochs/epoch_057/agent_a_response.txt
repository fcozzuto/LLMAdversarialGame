def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # maximize distance from opponent
            val = d2(nx, ny, ox, oy)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    # pick best target resource from our perspective but considering opponent pressure
    best_t = None
    best_t_val = None
    for rx, ry in resources:
        sd = d2(sx, sy, rx, ry)
        od = d2(ox, oy, rx, ry)
        # prefer where opponent is relatively far vs us; tie-break by being closer to us
        val = (od - sd, -sd)
        if best_t is None or val > best_t_val:
            best_t = (rx, ry)
            best_t_val = val

    tx, ty = best_t

    # choose move that best improves our position toward target while not letting opponent gain too much
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_to_t = d2(nx, ny, tx, ty)
        op_to_t = d2(ox, oy, tx, ty)
        # base: minimize our distance to target, maximize opponent relative disadvantage
        val = (-my_to_t + (op_to_t - my_to_t) // 4)
        # mild safety: prefer increasing distance from opponent
        val += d2(nx, ny, ox, oy) // 16
        # deterministic tie-break favoring staying/then smaller movement
        val_tuple = (val, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or val_tuple > best[0]:
            best = (val_tuple, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]