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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_target(tx, ty):
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        return (do - ds) * 10 - ds

    if resources:
        target = None
        best = -10**18
        for r in resources:
            val = score_target(r[0], r[1])
            if val > best or (val == best and r < target):
                best = val
                target = r
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = int(target[0]), int(target[1])

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        val = (-ds) * 5 + (do - ds) * 3
        if (nx, ny) == (tx, ty):
            val += 100000
        if val > best_val or (val == best_val and [dx, dy] < best_move):
            best_val = val
            best_move = [dx, dy]

    return best_move