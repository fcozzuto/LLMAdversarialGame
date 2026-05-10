def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    xp, yp = int(sp[0]), int(sp[1])

    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    resources_list = observation.get("resources", []) or []
    res = []
    for p in resources_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                res.append((int(p[0]), int(p[1])))
            except:
                pass

    opp = observation.get("opponent_position", [xp, yp]) or [xp, yp]
    ox, oy = int(opp[0]), int(opp[1])

    scores = observation.get("scores")
    if isinstance(scores, (list, tuple)) and len(scores) >= 2:
        aggressive = 1 if float(scores[0]) >= float(scores[1]) else 0
    else:
        aggressive = 0

    tx, ty = ox, oy
    if res:
        if aggressive:
            m = 10**18
            for a, b in res:
                d = (a - xp) * (a - xp) + (b - yp) * (b - yp)
                if d < m:
                    m = d
                    tx, ty = a, b
        else:
            m = -1
            for a, b in res:
                d = (a - xp) * (a - xp) + (b - yp) * (b - yp)
                if d > m:
                    m = d
                    tx, ty = a, b

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    bestv = 10**18

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    for dx, dy in dirs:
        nx, ny = xp + dx, yp + dy
        if not ok(nx, ny):
            continue
        v = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if v < bestv:
            bestv = v
            best = [dx, dy]

    if best is None:
        for dx, dy in dirs:
            nx, ny = xp + dx, yp + dy
            if ok(nx, ny):
                return [dx, dy]
    return best if best is not None else [0, 0]