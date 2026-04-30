def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_target = None
    if resources:
        best_score = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; tie-break by closeness to us.
            key = (do - ds, -ds)
            if best_score is None or key > best_score:
                best_score = key
                best_target = (rx, ry)
    else:
        cx, cy = w // 2, h // 2
        best_target = (cx, cy) if (sx, sy) != (cx, cy) else (clamp(sx + (1 if sx < w - 1 else -1), 0, w - 1),
                                                          clamp(sy + (1 if sy < h - 1 else -1), 0, h - 1))

    tx, ty = best_target
    cur_dist = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Consider opponent pressure on the target.
        od = cheb(ox, oy, tx, ty)
        # Prefer moves that reduce our distance; if equal, prefer increasing opponent distance from target.
        key = (-(nd), (od - nd), -cheb(nx, ny, ox, oy), -abs(nx - tx) - abs(ny - ty))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move == (0, 0) and resources and cur_dist > 0:
        # If stuck (e.g., blocked), gently move toward the target via best among all valid moves.
        alt = None
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            nd = cheb(nx, ny, tx, ty)
            if bestd is None or nd < bestd:
                bestd = nd
                alt = (dx, dy)
        if alt is not None:
            return [int(alt[0]), int(alt[1])]

    return [int(best_move[0]), int(best_move[1])]