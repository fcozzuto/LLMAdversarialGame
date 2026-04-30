def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = w // 2, h // 2

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                v = -(abs(nx - cx) + abs(ny - cy)) + 0.15 * cheb(nx, ny, ox, oy)
                if v > bestv:
                    bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_target = None
    best_tv = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        tv = (do - ds) * 2 - ds + 0.1 * cheb(rx, ry, cx, cy)
        if tv > best_tv:
            best_tv, best_target = tv, (rx, ry)

    tx, ty = best_target
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        # Encourage getting closer to target and staying away from opponent
        v = -ds2 * 3 + (do2 * 0.35) - cheb(nx, ny, ox, oy) * 0.05
        # If stepping onto a resource, strongly prefer
        if (nx, ny) in obst:
            continue
        if (nx, ny) == (tx, ty):
            v += 1000
        # Mild center control to avoid corner trapping
        v += -0.02 * (abs(nx - cx) + abs(ny - cy))
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [int(best[0]), int(best[1])]