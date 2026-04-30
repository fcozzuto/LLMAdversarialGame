def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def cheb(ax, ay, bx, by):
        da = ax - bx
        db = ay - by
        return abs(da) if abs(da) > abs(db) else abs(db)

    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Choose target resource to contest: prefer resources where we're closer than opponent.
    if resources:
        best_t = None
        best_k = None
        for (rx, ry) in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Smaller is better: self advantage dominates, but keep overall progress.
            k = (sd - od) + 0.12 * sd
            if best_k is None or k < best_k or (k == best_k and (rx, ry) < best_t):
                best_k = k
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = ox, oy

    # Greedy step toward target with deterministic tie-break; discourage moving away.
    best_move = [0, 0]
    best = None
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        step_cost = (nd - curd)
        # prefer decreasing distance; slight bias for progressing diagonally when tied
        diag_bias = 0 if dx == 0 or dy == 0 else -0.01
        # tie-break deterministically by move order
        score = (step_cost, nd, diag_bias, dx, dy)
        if best is None or score < best:
            best = score
            best_move = [dx, dy]
    return best_move