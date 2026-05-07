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
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cell_preference(rx, ry):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive is good (we arrive sooner)
        # primary: maximize lead, secondary: minimize our distance, tertiary: prefer closer to cornered opponent (deterministic tie)
        return (-lead, sd, (rx + ry) & 7)

    target = min(resources, key=lambda c: cell_preference(c[0], c[1]))
    tx, ty = target

    dx_des = 0 if tx == sx else (1 if tx > sx else -1)
    dy_des = 0 if ty == sy else (1 if ty > sy else -1)

    moves = []
    # order deterministic: prefer desired diagonal, then horizontal/vertical, then others, then stay last
    cand = [(dx_des, dy_des), (dx_des, 0), (0, dy_des), (dx_des, -dy_des), (-dx_des, dy_des), (-dx_des, 0), (0, -dy_des), (-dx_des, -dy_des), (0, 0)]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if dx in (-1, 0, 1) and dy in (-1, 0, 1) and inb(nx, ny):
            # evaluate move by resulting distance advantage, but no deeper search
            nsd = cheb(nx, ny, tx, ty)
            nod = cheb(ox, oy, tx, ty)
            moves.append(((-(nod - nsd)), nsd, nx, ny))

    if not moves:
        return [0, 0]
    _, _, bestx, besty = min(moves)
    return [bestx - sx, besty - sy]