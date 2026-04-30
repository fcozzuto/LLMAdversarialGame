def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_threat = None
    opp_best = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d <= 2 and d < opp_best:
            opp_best = d
            opp_threat = (rx, ry)
    if opp_threat is None:
        opp_threat = min(resources, key=lambda r: (cheb(ox, oy, r[0], r[1]), r[0], r[1]))

    best = (0, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_adv = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = (opd - myd) * 120 - myd * 3
            if (rx, ry) == opp_threat:
                adv += 250 - myd * 10  # contest immediate opponent target
            adv += (rx * 2 + ry) * 0.001
            if adv > best_adv:
                best_adv = adv

        key = (best_adv, -cheb(nx, ny, opp_threat[0], opp_threat[1]), -nx - ny)
        if key > best[1:]:
            best = ((dx, dy), key[0])

    return [best[0][0], best[0][1]] if isinstance(best[0], tuple) else [0, 0]