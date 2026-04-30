def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        best_t = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - do, ds, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
        cur_ds = cheb(sx, sy, tx, ty)
        best_m = None
        best_sc = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            nds = cheb(nx, ny, tx, ty)
            ods = cheb(ox, oy, tx, ty)
            sc = (cur_ds - nds, -nds, -(abs(nx - ox) + abs(ny - oy)), dx == 0 and dy == 0)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best_m = [dx, dy]
        return best_m

    # No visible resources: move away from opponent if possible, else stay
    best_m = None
    best_d = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, ox, oy)
        if best_d is None or d > best_d or (d == best_d and (dx, dy) == (0, 0)):
            best_d = d
            best_m = [dx, dy]
    return best_m