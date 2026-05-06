def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    try:
        w = int(w)
        h = int(h)
    except:
        return [0, 0]
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    try:
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except:
        return [0, 0]
    if w <= 0 or h <= 0:
        return [0, 0]

    obst = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            obst.add((x, y))
        except:
            pass

    def parse_xy(item):
        try:
            return int(item[0]), int(item[1])
        except:
            return None

    resources = []
    for r in observation.get("resources") or []:
        xy = parse_xy(r)
        if xy is not None:
            resources.append(xy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources closer to us; break ties by making opponent farther.
            key = (sd, -od, rx, ry)
            if best is None or key < best:
                best = key
                target = (rx, ry)

    def valid_step(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obst

    if target is None:
        for dx, dy in moves:
            if valid_step(dx, dy):
                return [dx, dy]
        return [0, 0]

    rx, ry = target
    best_move = None
    best_key = None
    for dx, dy in moves:
        if not valid_step(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        dist = cheb(nx, ny, rx, ry)
        # Deterministic: lower dist, then lower dist for opponent, then dx,dy preference.
        odist = cheb(ox, oy, rx, ry)
        key = (dist, -odist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        for dx, dy in moves:
            if valid_step(dx, dy):
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]