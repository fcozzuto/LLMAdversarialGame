def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def score_cell(x, y, target):
        tx, ty = target
        dx = x - tx
        if dx < 0:
            dx = -dx
        dy = y - ty
        if dy < 0:
            dy = -dy
        d = dx if dx >= dy else dy
        ox2 = x - ox
        if ox2 < 0:
            ox2 = -ox2
        oy2 = y - oy
        if oy2 < 0:
            oy2 = -oy2
        od = ox2 if ox2 >= oy2 else oy2
        return d * 10 - od

    best = (10**18, 0, 0)
    if resources:
        target = min(resources, key=lambda t: score_cell(t[0], t[1], (sx, sy)))
        target = None
        best_target = None
        best_d = 10**18
        for t in resources:
            tx, ty = t
            dx = sx - tx
            if dx < 0:
                dx = -dx
            dy = sy - ty
            if dy < 0:
                dy = -dy
            d = dx if dx >= dy else dy
            if d < best_d:
                best_d = d
                best_target = t
        target = best_target
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if inside(nx, ny) and (nx, ny) not in obstacles:
                sc = score_cell(nx, ny, target)
                if sc < best[0] or (sc == best[0] and (dxm, dym) < (best[1], best[2])):
                    best = (sc, dxm, dym)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if inside(nx, ny) and (nx, ny) not in obstacles:
                dxc = nx - cx
                if dxc < 0:
                    dxc = -dxc
                dyc = ny - cy
                if dyc < 0:
                    dyc = -dyc
                dc = dxc if dxc >= dyc else dyc
                odx = nx - ox
                if odx < 0:
                    odx = -odx
                ody = ny - oy
                if ody < 0:
                    ody = -ody
                od = odx if odx >= ody else ody
                sc = dc * 10 - od
                if sc < best[0] or (sc == best[0] and (dxm, dym) < (best[1], best[2])):
                    best = (sc, dxm, dym)

    dxm, dym = int(best[1]), int(best[2])
    if dxm < -1:
        dxm = -1
    elif dxm > 1:
        dxm = 1
    if dym < -1:
        dym = -1
    elif dym > 1:
        dym = 1
    if (sx + dxm, sy + dym) in obstacles or not inside(sx + dxm, sy + dym):
        return [0, 0]
    return [dxm, dym]