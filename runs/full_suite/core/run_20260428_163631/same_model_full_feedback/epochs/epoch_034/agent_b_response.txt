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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            res_prog = -cheb(nx, ny, tx, ty)
            opp_safe = cheb(nx, ny, ox, oy)
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            key = (res_prog, opp_safe, -stay_pen, -dx, -dy)
            if best is None or key > best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        d_res = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < d_res:
                d_res = d
        d_opp = cheb(nx, ny, ox, oy)

        key = (-d_res, d_opp, 0 if (dx == 0 and dy == 0) else -1, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]