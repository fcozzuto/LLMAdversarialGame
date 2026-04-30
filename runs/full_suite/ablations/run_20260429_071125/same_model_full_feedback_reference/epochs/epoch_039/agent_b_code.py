def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    tx, ty = None, None
    if resources:
        best = None
        for x, y in resources:
            ds = abs(x - sx) + abs(y - sy)
            do = abs(x - ox) + abs(y - oy)
            # prefer resources we can reach no later than opponent, then smaller ds, then lexicographic
            score = (-(do - ds >= 0), ds, x, y)
            if best is None or score < best:
                best = score
                tx, ty = x, y
    if tx is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        # small preference to avoid stepping into worse positions vs opponent
        adv = (abs(nx - ox) - abs(nx - sx))
        key = (d, -adv, nx, ny, dx, dy)
        if best_move is None or key < best_move:
            best_move = key
            best_dx, best_dy = int(dx), int(dy)

    if best_move is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    return [best_dx, best_dy]