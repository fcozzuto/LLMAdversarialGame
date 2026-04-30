def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # pick a target resource where we have an advantage (or least deficit)
    tx, ty = sx, sy
    if resources:
        best = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # higher is better: our closeness + advantage
            val = (dop - dme) * 3 - dme
            if best is None or val > best[0] or (val == best[0] and dme < best[1]):
                best = (val, dme, rx, ry)
        tx, ty = best[2], best[3]
    else:
        tx, ty = w // 2, h // 2

    # evaluate immediate move
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dme = cheb(nx, ny, tx, ty)
        dop = cheb(ox, oy, tx, ty)

        # keep pressure on opponent: prefer moves that improve our advantage and increase distance to opponent when idle
        opp_dist = cheb(nx, ny, ox, oy)
        adv = (dop - dme)
        score = adv * 10 - dme + (opp_dist if (tx, ty) == (w // 2, h // 2) else opp_dist // 2)

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]