def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if inb(bx, by):
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry):
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def adv_to(rx, ry):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        return myd - opd, myd, rx, ry

    resources.sort(key=adv_to)
    tx, ty = resources[0]

    step_x = 1 if tx > sx else (-1 if tx < sx else 0)
    step_y = 1 if ty > sy else (-1 if ty < sy else 0)

    moves = [(step_x, step_y), (step_x, 0), (0, step_y), (-step_x, 0), (0, -step_y), (0, 0),
             (1 if step_x == 0 else -step_x, 1 if step_y == 0 else 0),
             (-1 if step_x == 0 else step_x, -1 if step_y == 0 else 0),
             (1 if step_x == 0 else 0, 1 if step_y == 0 else -step_y)]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        key = (d_self - d_opp, d_self, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    return [dx, dy]
        return [0, 0]
    return [best[1], best[2]]