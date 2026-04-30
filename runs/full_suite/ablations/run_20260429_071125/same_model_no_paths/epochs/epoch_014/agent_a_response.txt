def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    def score_target(t):
        myd = dist((sx, sy), t)
        opd = dist((ox, oy), t)
        return (opd - myd, -myd, t[0], t[1])  # prefer my advantage, then closer

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_t = None
        best_key = None
        for t in resources:
            key = score_target(t)
            if best_key is None or key > best_key:
                best_key, best_t = key, t

        tx, ty = best_t
        best_move = [0, 0]
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            myd2 = dist((nx, ny), (tx, ty))
            opd2 = dist((ox, oy), (tx, ty))
            # also slight preference for moves that reduce opponent distance to the same target less than ours
            val = (opd2 - myd2, -myd2, -abs(nx - tx) - abs(ny - ty), dx, dy)
            if best_val is None or val > best_val:
                best_val, best_move = val, [dx, dy]
        return best_move

    # No visible resources: drift to the side more likely to collect by being closer overall
    targets = [(0, 0), (w - 1, h - 1), (0, h - 1), (w - 1, 0), (w // 2, h // 2)]
    # pick corner based on who is closer to each
    best = None
    best_key = None
    for t in targets:
        if 0 <= t[0] < w and 0 <= t[1] < h and t not in blocked:
            myd = dist((sx, sy), t)
            opd = dist((ox, oy), t)
            key = (opd - myd, -myd, t[0], t[1])
            if best_key is None or key > best_key:
                best_key, best = key, t
    tx, ty = best
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        val = (-dist((nx, ny), (tx, ty)), dx, dy)
        if best_val is None or val > best_val:
            best_val, best_move = val, [dx, dy]
    return best_move if best_val is not None else [0, 0]