def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    x, y = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    x, y, ox, oy = int(x), int(y), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if t not in obs:
                res.append(t)
                resset.add(t)

    if w <= 0 or h <= 0:
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves.sort(key=lambda t: (t[0], t[1]))

    if not res:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not ok(nx, ny):
                continue
            v = -man(nx, ny, ox, oy)  # drift away from opponent
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not ok(nx, ny):
            continue
        val = 0
        if (nx, ny) in resset:
            val += 10**9
        best_res = 10**18
        for rx, ry in res:
            dme = man(nx, ny, rx, ry)
            if dme < best_res:
                best_res = dme
                bre = (rx, ry)
        if best_res < 10**18:
            rx, ry = bre
            opp = man(ox, oy, rx, ry)
            val += -best_res * 10 + opp * 2
        val += -(abs(nx - ox) + abs(ny - oy)) // 3  # slight distancing
        if val > bestv:
            bestv = val
            best = [dx, dy]
    return best