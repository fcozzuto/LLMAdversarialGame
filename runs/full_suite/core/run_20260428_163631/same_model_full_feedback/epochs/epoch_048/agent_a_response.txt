def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    t = int(observation.get("turn_index") or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corner_targets = [(0, h - 1), (w - 1, 0), (0, 0), (w - 1, h - 1)]
    bias = corner_targets[t % 4]

    if not resources:
        tx, ty = bias
        best = (0, 0)
        bestd = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best_res = None
    best_adv = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive means we're closer
        if best_adv is None or adv > best_adv or (adv == best_adv and (sd < cheb(sx, sy, best_res[0], best_res[1]) if best_res else True)):
            best_adv = adv
            best_res = (rx, ry)
    tx, ty = best_res

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # primary: move toward our chosen target; secondary: keep/increase our advantage vs opponent
        score = (sd2, -((od2 - sd2) * 1000 + (tx + ty) % 3), (dx, dy) == (0, 0))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]