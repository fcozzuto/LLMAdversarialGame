def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [W - 1, H - 1]) or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))
    ox, oy = int(op[0]), int(op[1])

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_adj_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obstacles:
                    pen += 1
        return pen

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    if not resources:
        tx, ty = W // 2, H // 2
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty) - 0.2 * obstacle_adj_pen(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [int(best[0]), int(best[1])]

    best_res = resources[0]
    bestv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        v = (opd - myd) * 10 - 0.5 * obstacle_adj_pen(rx, ry)
        if v > bestv:
            bestv, best_res = v, (rx, ry)

    rx, ry = best_res
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, rx, ry)
        opd2 = cheb(ox, oy, rx, ry)
        step_improve = (cheb(sx, sy, rx, ry) - myd2)
        v = (opd2 - myd2) * 10 + step_improve * 3 - 0.7 * obstacle_adj_pen(nx, ny)
        if (dx, dy) == (0, 0) and step_improve > 0:
            v -= 0.5
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]