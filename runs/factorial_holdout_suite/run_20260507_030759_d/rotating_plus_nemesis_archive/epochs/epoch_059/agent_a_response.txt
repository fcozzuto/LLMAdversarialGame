def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # win if we arrive no later than opponent; tie-break by our speed, then opponent slowness
        win = 1 if ds <= do else 0
        key = (0 if win else 1, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic: evaluate all 9 moves; choose minimal (avoid losing race first, then reduce distance to target).
    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue
        ns = cheb(nx, ny, tx, ty)
        # approximation of race: compare our next distance vs opponent current distance
        do = cheb(ox, oy, tx, ty)
        win = 1 if ns <= do else 0
        mk = (0 if win else 1, ns, -do, dx, dy)
        if bestmk is None or mk < bestmk:
            bestmk = mk
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]