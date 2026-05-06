def choose_move(observation):
    def to_int(v, d=0):
        try:
            return int(v)
        except:
            return d

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = to_int(sx), to_int(sy), to_int(ox), to_int(oy)

    w = to_int(observation.get("grid_width", 8), 8) or 8
    h = to_int(observation.get("grid_height", 8), 8) or 8

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = to_int(p[0]), to_int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            key = (cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    best_target = None
    best_key = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = to_int(r[0]), to_int(r[1])
        if not inb(rx, ry):
            continue
        ourd = cheb(sx, sy, rx, ry)
        oppd = cheb(ox, oy, rx, ry)
        if best_key is None:
            best_key = (- (oppd - ourd), ourd, rx * 1000 + ry)
            best_target = (rx, ry)
        else:
            key = (- (oppd - ourd), ourd, rx * 1000 + ry)
            if key < best_key:
                best_key = key
                best_target = (rx, ry)

    rx, ry = best_target if best_target is not None else (sx, sy)

    best_move = None
    best_mkey = None
    for dx, dy, nx, ny in legal:
        ourd2 = cheb(nx, ny, rx, ry)
        oppd2 = cheb(nx, ny, ox, oy)
        key = (ourd2, -oppd2, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]