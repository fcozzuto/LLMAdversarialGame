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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_step(nx, ny, tx, ty):
        d_cur = abs(sx - tx) + abs(sy - ty)
        d_new = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        return (d_cur - d_new) * 100 - d_opp

    if resources:
        target = min(resources, key=lambda t: (abs(sx - t[0]) + abs(sy - t[1]), t[0], t[1]))
        tx, ty = target
        best = None
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            s = score_step(nx, ny, tx, ty)
            if s > best_s or (s == best_s and (dx, dy) < best):
                best_s = s
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    # No reachable resources (or none given): deterministically move toward opponent if possible
    tx, ty = ox, oy
    best = None
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = (abs(sx - ty) + abs(sy - tx)) - (abs(nx - ty) + abs(ny - tx))
        s = s * 100 - (abs(nx - ox) + abs(ny - oy))
        if s > best_s or (s == best_s and (dx, dy) < best):
            best_s = s
            best = (dx, dy)
    return [0, 0] if best is None else [best[0], best[1]]