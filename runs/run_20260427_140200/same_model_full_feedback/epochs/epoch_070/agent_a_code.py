def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    if not resources:
        resources = [(ox, oy)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_sd = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -sd, -tx, -ty)
        if best is None or key > best:
            best = key
            best_sd = sd
            best_t = (tx, ty)

    tx, ty = best_t

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    chosen = None
    chosen_dist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        if chosen is None or d < chosen_dist:
            chosen = (dx, dy)
            chosen_dist = d

    if chosen is None:
        return [0, 0]
    return [int(chosen[0]), int(chosen[1])]