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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_score_from(px, py):
        if not resources:
            return -10**9, 10**9, 10**9
        best = None
        best_self_d = 10**9
        best_opp_d = 10**9
        for tx, ty in resources:
            sd = cheb(px, py, tx, ty)
            od = cheb(ox, oy, tx, ty)
            sc = od - sd
            if best is None or sc > best[0] or (sc == best[0] and (sd < best_self_d or (sd == best_self_d and (ty < best[2] or (ty == best[2] and tx < best[1]))))):
                best = (sc, tx, ty)
                best_self_d = sd
                best_opp_d = od
        return best[0], best[1], best[2]

    if not resources:
        # deterministic "stay near center" move
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, [0, 0])
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best[0]:
                best = (d, [dx, dy])
        return best[1]

    cur_sc, tx, ty = best_score_from(sx, sy)

    best_move = [0, 0]
    best_tuple = (-10**9, 10**9, 10**9)  # (score, self_d, move_order)
    for i, (dx, dy) in enumerate(dirs):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc, ntx, nty = best_score_from(nx, ny)
        sd = cheb(nx, ny, ntx, nty)
        tup = (sc, sd, i)
        if tup > best_tuple:
            best_tuple = tup
            best_move = [dx, dy]

    return best_move