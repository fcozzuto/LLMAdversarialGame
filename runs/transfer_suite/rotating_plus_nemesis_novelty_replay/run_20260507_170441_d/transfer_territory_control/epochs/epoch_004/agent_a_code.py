def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))
        except:
            pass

    un = set()
    un_cells = observation.get("unclaimed_cells", None)
    if un_cells:
        for p in un_cells:
            try:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) not in obs:
                    un.add((x, y))
            except:
                pass

    res = set()
    for p in observation.get("resources", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.add((x, y))
        except:
            pass

    opp_pen = 2
    steps = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_sc = -10**18
    for dx, dy in steps:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        md = abs(nx - ox) + abs(ny - oy)
        sc = -opp_pen * md
        if (nx, ny) in res:
            sc += 1000
        if (nx, ny) in un:
            sc += 300
        if un or res:
            target = None
            if (nx, ny) in res:
                target = (nx, ny)
            elif (nx, ny) in un:
                target = (nx, ny)
            if target is None:
                if res:
                    d = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
                    sc += max(0, 80 - d)
                if un:
                    d = min(abs(nx - ux) + abs(ny - uy) for ux, uy in un)
                    sc += max(0, 40 - d)
        if best is None or sc > best_sc:
            best_sc = sc
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best