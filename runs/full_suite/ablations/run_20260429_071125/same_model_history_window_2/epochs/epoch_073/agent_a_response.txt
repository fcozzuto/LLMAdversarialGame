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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if any((x == sx and y == sy) for x, y in resources):
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    target = None
    if resources:
        best = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            # Prefer close resources, and also those the opponent is farther from.
            val = ds - 0.9 * do + 0.001 * (x + 0.5 * y)
            key = (-val, x, y)  # deterministic tie-break
            if best is None or key > best[0]:
                best = (key, (x, y))
        target = best[1]
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = int(target[0]), int(target[1])
    curd = cheb(sx, sy, tx, ty)
    safest = (10**9, -1, 0, 0)  # (score, dist_opp, nx, ny)
    best_reduce = (10**9, -10**9, 0, 0)  # (dist, -dist_opp, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        dop = cheb(nx, ny, ox, oy)
        if nd < curd:
            # Strongly prefer moves that reduce distance to target.
            cand = (nd, -dop, nx, ny)
            if cand < best_reduce:
                best_reduce = cand
        # Also track overall safest reasonable move.
        # Prefer larger dop; break ties toward lower nd then deterministic by coords.
        score = nd - 0.25 * dop + 0.001 * (nx + 0.5 * ny)
        cand = (score, dop, nx, ny)
        if cand < safest:
            safest = cand

    if best_reduce[3] != 0 or best_reduce[2] != 0 or best_reduce != (10**9, -10**9, 0, 0):
        _, _, nx, ny = best_reduce
        return [nx - sx, ny - sy]
    _, _, nx, ny = safest
    return [nx - sx, ny - sy]