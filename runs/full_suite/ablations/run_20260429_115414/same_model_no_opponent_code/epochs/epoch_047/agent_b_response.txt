def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
    else:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive if we are closer than opponent
            inv = ds + 1
            val = lead * 100 - inv  # prioritize winning resources
            if (rx, ry) == (sx, sy):
                val += 10**6
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

    # Choose move that reduces distance to target and also avoids allowing opponent to steal it
    best_move = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        progress = (ds_now - ds_new)
        steal_risk = do - ds_new  # higher means we still beat opponent (good)
        center = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        sc = progress * 1000 + steal_risk * 50 - center
        if (nx, ny) == (tx, ty):
            sc += 10**5
        # If current target is not favorable, try to steal any immediate resource
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == 0:
                if cheb(ox, oy, rx, ry) >= 1:
                    sc += 2 * 10**5
                else:
                    sc += 10**4
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]