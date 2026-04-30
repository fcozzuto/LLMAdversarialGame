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

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    res_cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                res_cells.append((x, y))

    if not res_cells:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            v = -cheb(nx, ny, cx, cy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target that we can get sooner than the opponent (max distance advantage)
    best_t = res_cells[0]
    best_adv = -10**9
    for tx, ty in res_cells:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        tie = -cheb(tx, ty, cx, cy) * 0.01
        key = adv + tie
        if key > best_adv:
            best_adv = key
            best_t = (tx, ty)

    tx, ty = best_t
    best = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Maximize who is closer, then keep moving toward the chosen target, and avoid drifting to center too much
        score = (opd - myd) * 1000 - myd - 0.001 * cheb(nx, ny, cx, cy)
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]