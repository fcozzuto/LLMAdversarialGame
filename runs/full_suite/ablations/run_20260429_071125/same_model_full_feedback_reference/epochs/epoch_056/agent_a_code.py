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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # deterministic fallback: head toward center while avoiding obstacles
        cx, cy = w // 2, h // 2
        best = (10**9, 10**9)
        best_move = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            od = cheb(nx, ny, ox, oy)
            cand = (d, -od)
            if cand < best:
                best = cand
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    center = (w // 2, h // 2)
    best_val = (-10**18, 10**18)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Evaluate the best resource we could move toward from (nx,ny)
        best_res = (10**18, -10**18)  # (self_dist, opp_adv)
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            opp_adv = od - sd  # higher means we are relatively closer
            # small tiebreak toward center control
            cd = cheb(rx, ry, center[0], center[1])
            key = (sd + 0.08 * cd, -opp_adv)
            if key < (best_res[0] + 0.0, -best_res[1] + 0.0):
                best_res = (sd, opp_adv)
        sd, opp_adv = best_res
        # prefer immediate collection (sd==0), then relative advantage, then center
        dist_center = cheb(nx, ny, center[0], center[1])
        val = (10000 if sd == 0 else 0) + opp_adv * 100 + (-sd) * 2 + (-dist_center)
        # deterministic secondary: prefer smaller dx, then dy
        cand2 = (val, abs(dx) + abs(dy), dx, dy)
        if cand2 > best_val:
            best_val = cand2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]