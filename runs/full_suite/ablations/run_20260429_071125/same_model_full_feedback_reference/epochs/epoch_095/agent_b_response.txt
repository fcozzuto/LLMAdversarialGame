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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # flee/avoid opponent deterministically
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            cand = (d, - (dx == 0 and dy == 0), - (nx + ny))
            if best is None or cand > best[0]:
                best = (cand, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose move by selecting the best resource for us (considering opponent distance),
    # while also favoring higher immediate distance-from-opponent.
    opp_weight = 1.15
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate best target resource from this next position
        target_val = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            # lower is better for us: closer than opponent
            v = ds - opp_weight * do
            if target_val is None or v < target_val:
                target_val = v
        # Combine: improve target advantage, also keep away from opponent
        dist_opp = man(nx, ny, ox, oy)
        cand = (target_val, -dist_opp, abs(nx - sx) + abs(ny - sy), (nx, ny))
        if best_val is None or cand < best_val:
            best_val = cand
            best_move = [dx, dy]
    return best_move if legal(sx + best_move[0], sy + best_move[1]) else [0, 0]