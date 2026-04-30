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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources remain, maximize distance from opponent deterministically.
    if not resources:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = cheb(nx, ny, ox, oy)
            cand = (val, dx, dy)
            if best is None or cand > best:
                best = cand
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    alpha = 0.15
    beta = 0.05

    best = None
    # Prefer moves that can reach a resource quickly; break ties by distancing from opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dres = min(cheb(nx, ny, tx, ty) for tx, ty in resources)
        dop = cheb(nx, ny, ox, oy)
        # Small incentive to avoid staying too long near the opponent's closest approach.
        # Deterministic tie-break: higher score, then lex (dx,dy).
        val = (-dres) + alpha * dop - beta * cheb(ox, oy, nx, ny)
        cand = (val, dx, dy)
        if best is None or cand > best:
            best = cand

    return [best[1], best[2]] if best is not None else [0, 0]