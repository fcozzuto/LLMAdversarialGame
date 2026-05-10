def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obs.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))

    if not res:
        tx, ty = (w // 2), (h // 2)
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = - (abs(tx - nx) + abs(ty - ny))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    def mdist(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        # Prefer moves that become closer than opponent to some resource (relative advantage),
        # with tie-break: prefer lower own distance.
        best_rel = -10**18
        best_selfd = 10**18
        for rx, ry in res:
            sd = mdist(nx, ny, rx, ry)
            od = mdist(ox, oy, rx, ry)
            rel = od - sd
            if rel > best_rel or (rel == best_rel and sd < best_selfd):
                best_rel = rel
                best_selfd = sd
        v = (best_rel * 1000) - best_selfd
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best