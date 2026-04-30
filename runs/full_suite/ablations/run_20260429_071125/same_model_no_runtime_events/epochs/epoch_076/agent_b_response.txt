def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_obst(x, y):
        c = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    c += 1
        return c

    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
        dself = cheb(nx, ny, ox, oy)  # how close we are to opponent
        obst_pen = adj_obst(nx, ny) * 0.35

        # target evaluation: prefer states where we can reach a resource sooner than opponent
        val = -dself * 0.12 - obst_pen
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # score: distance advantage + slight preference toward resources near center
            adv = (od - sd)
            if adv >= 0:
                v = 6.0 + adv * 1.6 - sd * 0.15
            else:
                v = adv * 2.0 - sd * 0.25
            ccx = rx - cx
            if ccx < 0: ccx = -ccx
            ccy = ry - cy
            if ccy < 0: ccy = -ccy
            v -= (ccx + ccy) * 0.02
            # also prefer not to allow opponent too close to same resource
            v -= max(0, od - 1) * 0.03
            if v > val:
                val = v

        if best_val is None or val > best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]