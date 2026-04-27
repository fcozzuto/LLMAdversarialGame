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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources.sort()

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - md, -md, rx, ry)  # prefer we are closer than opponent; then closer overall
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        best_move = (0, 0)
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                nd = cheb(nx, ny, tx, ty)
                my_d = cheb(nx, ny, tx, ty)
                op_d = cheb(ox, oy, tx, ty)
                val = (op_d - my_d, -my_d, -abs((nx - tx)) - abs((ny - ty)), dx, dy)
                if best_val is None or val > best_val:
                    best_val = val
                    best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward center but also reduce cheb to opponent corner if needed.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    target = (cx, cy) if cheb(sx, sy, cx, cy) <= cheb(ox, oy, cx, cy) else (cx, cy)
    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            nd = cheb(nx, ny, tx, ty)
            val = (-nd, dx, dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]