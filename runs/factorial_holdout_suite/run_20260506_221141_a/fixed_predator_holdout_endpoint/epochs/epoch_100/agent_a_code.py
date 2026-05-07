def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = ((od - sd) * 10 - sd, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r[0], best_r[1]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    prefs = [(dx, dy)]
    for a, b in [(dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        if (a, b) not in prefs:
            prefs.append((a, b))

    best_move = (0, 0)
    best_mkey = None
    for mdx, mdy in prefs:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        my_closer = nd <= cheb(sx, sy, tx, ty)
        mkey = (my_closer, (od - nd) * 10 - nd, -nd, mdx, mdy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]