def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                if not (x == sx and y == sy):
                    resources.append((x, y))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            nx = x + ddx
            if nx < 0 or nx >= w:
                continue
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ny = y + ddy
                if 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    target = None
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        c = myd - 0.9 * opd + 1.2 * adj_obst(rx, ry)
        if best is None or c < best or (c == best and (rx < target[0] or (rx == target[0] and ry < target[1]))):
            best = c
            target = (rx, ry)

    rx, ry = target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                myd = cheb(nx, ny, rx, ry)
                step_bad = 0.8 * adj_obst(nx, ny)
                block = 0
                if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy) and myd > cheb(sx, sy, rx, ry):
                    block = 0.3
                moves.append((myd + step_bad + block, cheb(nx, ny, ox, oy), dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(moves[0][2]), int(moves[0][3])]