def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        # Pick resource with maximum advantage over opponent; tie-break by closeness to self.
        best = None
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            # small center bias to avoid dithering
            cb = -(abs(rx - w/2) + abs(ry - h/2)) * 0.01
            score = (do - ds) + cb
            cand = (score, -ds, -rx, -ry)
            if best is None or cand > best[0]:
                best = (cand, rx, ry)
        tx, ty = best[1], best[2]

    # Choose move that reduces distance to target, prefers blocking opponent a bit.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = md(nx, ny, tx, ty)
        curd = md(sx, sy, tx, ty)
        # opponent distance estimate from their current position (we can't move-forecast deterministically)
        do = md(ox, oy, tx, ty)
        # try to improve our lead and make it harder for opponent to reach the target
        key = (
            -ds,
            -(do - ds),
            -((nx - w/2) ** 2 + (ny - h/2) ** 2),
            -((dx != 0) or (dy != 0)),
            curd == ds
        )
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]