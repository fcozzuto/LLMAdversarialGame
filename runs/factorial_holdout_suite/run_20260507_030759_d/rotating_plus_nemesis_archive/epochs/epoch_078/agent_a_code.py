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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        lead = od - sd
        # Prefer we can arrive first or at least tie; otherwise minimize our loss.
        # Tie-break by closeness (smaller sd).
        key = (lead, -sd, -cheb(tx, ty, w - 1 - ox, h - 1 - oy))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    curd = cheb(sx, sy, tx, ty)
    bestm = (0, 0)
    bestd = curd + 999999
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer strictly improving, then smaller remaining distance, then deterministic direction order.
        if nd < bestd:
            bestd = nd
            bestm = (dx, dy)
        elif nd == bestd:
            if (dx, dy) < bestm:
                bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]