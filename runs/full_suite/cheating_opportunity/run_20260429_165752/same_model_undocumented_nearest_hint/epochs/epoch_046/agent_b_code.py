def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        # Pick a target that we are closest to (tie-break by worse opponent proximity).
        best_t = resources[0]
        best = None
        for (tx, ty) in resources:
            d1 = cheb(sx, sy, tx, ty)
            d2 = cheb(ox, oy, tx, ty)
            key = (d1, -d2)
            if best is None or key < best:
                best, best_t = key, (tx, ty)
    else:
        # No visible resources: move toward opponent or stay if blocked.
        best_t = (ox, oy)

    tx, ty = best_t
    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # Prefer capturing: landing on a resource gets big bonus.
        cap = 1 if resources and (nx, ny) in set(resources) else 0
        # Also prefer moves that reduce our distance to target.
        score = (cap * 100000) - d_self * 10 - (cheb(nx, ny, ox, oy))
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move if best_score is not None else [0, 0]