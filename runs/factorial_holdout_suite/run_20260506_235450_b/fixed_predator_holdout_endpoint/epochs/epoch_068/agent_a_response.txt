def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_list = []
    for r in resources:
        if len(r) >= 2 and inb(r[0], r[1]):
            t = (r[0], r[1])
            if t not in obstacles:
                res_list.append(t)
    if not res_list:
        return [0, 0]

    best = None
    best_key = None
    for tx, ty in res_list:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer being no worse than opponent (denier opponent), then closer overall.
        # Deterministic tie-break by coords.
        key = ((opd - myd) * 100 - myd, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Keep advantage; if equal, go for progress.
        val = ((opd - myd2) * 100 - myd2, -myd2, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]