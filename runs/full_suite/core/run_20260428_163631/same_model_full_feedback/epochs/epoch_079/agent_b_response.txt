def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best_r = None
        best_sc = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            sc = (od - myd) * 10 - myd
            if best_sc is None or sc > best_sc or (sc == best_sc and (rx, ry) < best_r):
                best_sc = sc
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # Prefer moves that (1) get closer to target, (2) reduce opponent's advantage
        oppd = cheb(ox, oy, tx, ty)
        myd = cheb(nx, ny, tx, ty)
        advantage = (oppd - myd) * 10
        val = advantage - dist
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]