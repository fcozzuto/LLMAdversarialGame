def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = [0, 0]
    bestv = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        if not res:
            v = cheb(nx, ny, int(round(cx)), int(round(cy))) * 0.2 + cheb(nx, ny, ox, oy) * 0.05
            if v > bestv:
                bestv = v
                best_move = [dx, dy]
            continue

        vbest = -10**18
        for rx, ry in res:
            dme = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            adv = dop - dme  # positive => contest/grab sooner
            if dme == 0:
                adv += 10  # prefer immediate pickup
            val = 2.5 * adv - dme
            if val > vbest:
                vbest = val

        v = vbest + 0.15 * cheb(nx, ny, ox, oy)  # slight safety vs center_rush rushes
        if v > bestv:
            bestv = v
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]