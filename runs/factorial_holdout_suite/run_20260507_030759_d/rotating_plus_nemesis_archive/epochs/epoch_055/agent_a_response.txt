def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    best = None
    best_key = None
    for rx, ry in res:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        dist_center = abs(rx - cx) + abs(ry - cy)
        key = (od - sd, -sd, dist_center)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if tx == sx and ty == sy:
        return [0, 0]

    def step_toward(tx, ty):
        dx = 0
        if tx > sx:
            dx = 1
        elif tx < sx:
            dx = -1
        dy = 0
        if ty > sy:
            dy = 1
        elif ty < sy:
            dy = -1
        return dx, dy

    dx, dy = step_toward(tx, ty)
    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
        return [dx, dy]

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_m = (0, 0)
    best_md = 10**9
    for mx, my in moves:
        px, py = sx + mx, sy + my
        if 0 <= px < w and 0 <= py < h and (px, py) not in obst:
            md = cheb(px, py, tx, ty)
            if md < best_md or (md == best_md and (mx, my) < best_m):
                best_md = md
                best_m = (mx, my)
    return [int(best_m[0]), int(best_m[1])]