def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w // 2), (h // 2)
        bestd, bestmove = None, (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestmove):
                bestd, bestmove = d, (dx, dy)
        return [int(bestmove[0]), int(bestmove[1])]

    best_target = None
    best_adv = None
    for rx, ry in resources:
        our_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        adv = opp_d - our_d
        if best_adv is None or adv > best_adv or (adv == best_adv and (rx, ry) < best_target):
            best_adv, best_target = adv, (rx, ry)
    tx, ty = best_target

    best_score = None
    bestmove = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_our = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        adv = d_opp - d_our  # higher is better: closer than opponent to target
        # mild tie-breaks: avoid getting closer to opponent if we're not winning the target
        opp_close = cheb(nx, ny, ox, oy)
        score = (adv * 1000) - d_our - (1 if adv < 0 else 0) * opp_close
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < bestmove):
            best_score, bestmove = score, (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]