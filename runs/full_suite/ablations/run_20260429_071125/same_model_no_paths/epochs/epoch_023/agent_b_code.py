def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w)
    h = int(h)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_res = None
    best_d = 10**9
    for (rx, ry) in resources:
        d = cheb(sx, sy, rx, ry)
        if d < best_d:
            best_d = d
            best_res = (rx, ry)
        elif d == best_d and best_res is not None:
            if (rx, ry) < best_res:
                best_res = (rx, ry)

    if best_res is None:
        best_move = (0, 0)
        best_key = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_to_opp = cheb(nx, ny, ox, oy)
            key = (d_to_opp, -cheb(nx, ny, sx, sy), -dx*dx-dy*dy)
            if key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    rx, ry = best_res
    cur_d = cheb(sx, sy, rx, ry)
    best_move = (0, 0)
    best_key = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        improve = cur_d - d
        key = (improve, d_opp, -abs(nx - rx) - abs(ny - ry))
        if key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]