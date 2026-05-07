def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for t in observation.get("obstacles") or []:
        try:
            bx, by = int(t[0]), int(t[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
        except:
            pass
    if not resources:
        return [0, 0]

    best = None  # (do-ds, -ds, rx, ry)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        cand = (do - ds, -ds, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer getting closer; if equal, prefer keeping opponent further via do-ds after move.
        val = ((do - ds), -ds, -cheb(nx, ny, tx, ty))
        if best_move is None or val > best_move[0]:
            best_move = (val, dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[1]), int(best_move[2])]