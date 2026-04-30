def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if res:
        tx, ty = min(res, key=lambda r: abs(r[0] - sx) + abs(r[1] - sy))
        best = None
        best_score = -10**18
        for dx, dy, nx, ny in candidates:
            d_self = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            s = (-d_self) + 0.01 * ((d_opp - d_self))
            # small tie-breaker: prefer staying close to opponent to reduce their contest
            s += -0.001 * (abs(nx - ox) + abs(ny - oy))
            if best is None or s > best_score:
                best_score = s
                best = [dx, dy]
        return best

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        s = -d_to_opp  # chase if no resources
        if best is None or s > best_score:
            best_score = s
            best = [dx, dy]
    return best