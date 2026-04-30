def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        bx, by = tx, ty
    else:
        # Pick a resource where we have (or can quickly gain) advantage over opponent.
        best = None
        best_val = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where our relative closeness is better; tie-break by overall closeness.
            val = (do - ds, -(ds + do), -rx, -ry)
            if best_val is None or val > best_val:
                best_val = val
                best = (rx, ry)
        bx, by = best

    best_score = None
    best_move = (0, 0)
    # Deterministic tie-break: prefer moves with earlier ordering if equal score.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds = cheb(nx, ny, bx, by)
        do = cheb(ox, oy, bx, by)

        # Main: maximize advantage at target.
        score = (do - ds)
        # Secondary: also reduce distance to any remaining resource (small weight).
        if resources:
            dmin = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if dmin is None or d < dmin:
                    dmin = d
            score = score * 100 - (dmin if dmin is not None else 0)
        # Discourage wasting by standing still when alternatives exist.
        if dx == 0 and dy == 0:
            score -= 1

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]