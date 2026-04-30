def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, ox, oy)
            k = (-d, nx, ny)  # deterministically drift away from opponent
            if best is None or k < best[0]:
                best = (k, (dx, dy))
        return list(best[1])

    # Choose resource where we are relatively closer than opponent
    best_res = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer advantage (opd - myd), then closer overall; deterministic tie-break by coords
        key = (-(opd - myd), myd, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (tx, ty)

    tx, ty = best_res
    # Greedy step toward target with deterministic tie-break
    best_move = None
    best_step_key = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Also prefer not moving toward being closer than opponent by picking smaller my distance
        key = (myd, -(opd - myd), nx, ny)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]