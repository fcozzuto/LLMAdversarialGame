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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_t = None
    best_sc = None
    for tx, ty in resources:
        selfd = cheb(sx, sy, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Prioritize cells where we're not slower than opponent; if none, still prefer best arrival advantage.
        sc = (oppd - selfd) * 10 - selfd
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_t = (tx, ty)

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = (0, 0)
    best_md = None
    for mx, my in moves:
        x, y = sx + mx, sy + my
        if not valid(x, y):
            continue
        md = cheb(x, y, tx, ty)
        if best_md is None or md < best_md:
            best_md = md
            best_mv = (mx, my)
    return [int(best_mv[0]), int(best_mv[1])]