def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick target resource (deterministic: lowest opponent-distance, then our-distance, then coords)
    if resources:
        bestt = None
        for rx, ry in resources:
            td = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od, td, rx, ry)
            if bestt is None or key < bestt[0]:
                bestt = (key, (rx, ry))
        tx, ty = bestt[1]
    else:
        # No resources: move to increase distance from opponent while still valid
        tx, ty = ox, oy

    bestm = None
    curd = cheb(sx, sy, tx, ty)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        if resources:
            # prefer smaller distance to target; tie-break: larger distance from opponent
            oppd = cheb(nx, ny, ox, oy)
            mkey = (nd, -oppd, dx, dy)
        else:
            # prefer larger distance from opponent
            oppd = nd
            mkey = (-oppd, dx, dy)
        if bestm is None or mkey < bestm[0]:
            bestm = (mkey, [dx, dy])

    if bestm is None:
        return [0, 0]
    return bestm[1]