def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_adv = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if best is None or adv > best_adv or (adv == best_adv and (sd < best[0] or (sd == best[0] and (rx, ry) < best[1]))):
                best = (sd, (rx, ry))
                best_adv = adv
        tx, ty = best[1]
    else:
        tx, ty = ox, oy

    if (tx, ty) == (sx, sy):
        return [0, 0]

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if resources:
            # recompute advantage to current best target; small lookahead to avoid obstacle traps
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            val = (od - sd, -sd)  # maximize advantage, then minimize self distance
        else:
            val = (-cheb(nx, ny, tx, ty),)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]