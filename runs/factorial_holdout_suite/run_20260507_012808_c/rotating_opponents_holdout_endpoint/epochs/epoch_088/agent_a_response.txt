def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, 10**9)
        bestm = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = (man(nx, ny, cx, cy), man(nx, ny, ox, oy), abs(nx - ox) + abs(ny - oy))
            if v < best:
                best, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    best_r = None
    bestv = (10**9, 10**9, 10**9)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        priority = 0 if ds <= do else 1
        v = (priority, ds, -do)
        if v < bestv:
            bestv = v
            best_r = (rx, ry)

    tx, ty = best_r
    best = (10**9, 10**9, 10**9, 10**9)
    bestm = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = man(nx, ny, tx, ty)
        do2 = man(nx, ny, ox, oy)
        opp_pressure = 0 if ds2 <= do2 else 1
        v = (opp_pressure, ds2, man(nx, ny, tx, ty) + (0 if do2 > ds2 else 1), -min(do2, 99))
        if v < best:
            best, bestm = v, (dx, dy)

    return [int(bestm[0]), int(bestm[1])]