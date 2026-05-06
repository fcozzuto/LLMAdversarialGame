def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sc = mdist(nx, ny, ox, oy)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best_dx, best_dy = 0, 0
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_op = mdist(nx, ny, ox, oy)
        best_adv = -10**9
        best_dist = 10**9
        for rx, ry in resources:
            ds = mdist(nx, ny, rx, ry)
            do = mdist(ox, oy, rx, ry)
            adv = do - ds  # positive means we can reach sooner than opponent (from their current pos)
            if adv > best_adv:
                best_adv = adv
                best_dist = ds
            elif adv == best_adv and ds < best_dist:
                best_dist = ds
        # primary: secure resources where we're ahead; secondary: minimize our distance; tertiary: avoid closeness to opponent
        sc = (200 if best_adv > 0 else 0) + best_adv * 10 - best_dist - d_op * 0.2
        # if opponent is extremely close, bias to increasing separation
        if d_op <= 2:
            sc += d_op * 3
        if sc > best_sc:
            best_sc = sc
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]