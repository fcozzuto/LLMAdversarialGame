def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda d: (abs(d[0]) + abs(d[1]), d[0], d[1]))

    if resources:
        best_r = None
        best_v = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            v = (od - sd) * 1000 - sd  # primary: beat opponent distance; secondary: be closer
            if best_v is None or v > best_v or (v == best_v and (rx, ry) < best_r):
                best_v = v
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox + 0, oy + 0, tx, ty)  # opponent position unchanged in this choice
        candidates.append((nsd, -nod, (dx, dy), abs(nx - tx) + abs(ny - ty)))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[3], t[2][0], t[2][1]))
    dx, dy = candidates[0][2]
    return [int(dx), int(dy)]