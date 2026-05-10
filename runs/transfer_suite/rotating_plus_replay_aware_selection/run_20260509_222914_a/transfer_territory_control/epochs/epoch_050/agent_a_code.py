def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0) or 8
    h = int(observation.get("grid_height", 0) or 0) or 8
    sp = observation.get("self_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if free(x, y):
                res.append((x, y))
    if not res:
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    x, y = int(p[0]), int(p[1])
                except:
                    continue
                if free(x, y):
                    res.append((x, y))
    if not res:
        res = [(sx, sy)]

    best = None
    bx, by = None, None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = min((abs(nx - x) + abs(ny - y) for x, y in res))
        score = d
        if best is None or score < best:
            best = score
            bx, by = dx, dy

    if bx is None:
        return [0, 0]
    return [int(bx), int(by)]