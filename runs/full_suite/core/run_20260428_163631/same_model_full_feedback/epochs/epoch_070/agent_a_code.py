def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_t = resources[0]
        for tx, ty in resources:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer taking resources closer than opponent; break ties by being closer yourself.
            score = (od - sd) * 1000 - sd
            if best is None or score > best:
                best = score
                best_t = (tx, ty)
        tx, ty = best_t
        best_move = (0, 0)
        best_ms = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            nsd = cheb(nx, ny, tx, ty)
            nod = cheb(ox, oy, tx, ty)
            ms = (nod - nsd) * 1000 - nsd
            if best_ms is None or ms > best_ms:
                best_ms = ms
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]
    else:
        # No resources visible: move toward center while keeping valid moves.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_d = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            if best_d is None or d < best_d:
                best_d = d
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]