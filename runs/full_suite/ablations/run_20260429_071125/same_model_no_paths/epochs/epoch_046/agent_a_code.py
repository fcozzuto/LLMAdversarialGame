def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not resources:
        # Move toward opponent to contest, avoid obstacles.
        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if best is None or (d, nx, ny) < best[0]:
                best = ((d, nx, ny), [dx, dy])
        return best[1] if best is not None else [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick target: best for us considering opponent pressure.
    best_targets = []
    for (rx, ry) in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources where we are not far behind opponent; tie-break by coordinate.
        priority = (ds - do, ds, rx, ry)
        best_targets.append((priority, (rx, ry)))
    best_targets.sort(key=lambda t: t[0])
    tx, ty = best_targets[0][1]

    best_move = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_us = man(nx, ny, tx, ty)
        d_op = man(ox, oy, tx, ty)
        # Small incentive to move where we beat/close gap; deterministic tie-break.
        key = (d_us - d_op, d_us, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]