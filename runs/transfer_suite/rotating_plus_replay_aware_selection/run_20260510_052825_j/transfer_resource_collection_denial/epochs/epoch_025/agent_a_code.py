def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    bestx = besty = None
    for p in resources:
        if not (isinstance(p, (list, tuple)) and len(p) >= 2):
            continue
        rx, ry = int(p[0]), int(p[1])
        if (rx, ry) in obs:
            continue
        d = abs(rx - sx) + abs(ry - sy)
        if best is None or d < best:
            best = d
            bestx, besty = rx, ry

    if bestx is None:
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return -10**9
        dist = abs(bestx - nx) + abs(besty - ny)
        opp = abs(ox - nx) + abs(oy - ny)
        return -dist + 0.05 * opp

    bestm = (0, 0)
    bests = -10**9
    for dx, dy in dirs:
        sc = score_move(dx, dy)
        if sc > bests:
            bests = sc
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]