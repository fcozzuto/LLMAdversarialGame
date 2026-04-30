def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res_cells.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not res_cells:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target we can likely reach first (opponent-distance advantage)
    best_target = res_cells[0]
    best_adv = -10**18
    best_selfd = 10**18
    for tx, ty in res_cells:
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_selfd):
            best_adv = adv
            best_selfd = sd
            best_target = (tx, ty)

    tx, ty = best_target

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Strongly prefer reducing distance to the target, and maintaining/creating lead over opponent
        myd = d
        oppd = cheb(ox, oy, tx, ty)
        lead = oppd - myd
        center_pen = cheb(nx, ny, cx, cy)
        v = (0 if (nx == tx and ny == ty) else 0)
        v += 1000 if (nx == tx and ny == ty) else 0
        v += lead * 50
        v += -myd * 10
        v += -center_pen
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]