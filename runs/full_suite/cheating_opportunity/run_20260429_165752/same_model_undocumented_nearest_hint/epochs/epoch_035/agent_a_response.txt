def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def block_pen(x, y):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    pen += 2
        return pen

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            my_best = 10**9
            opp_best = 10**9
            lead_best = -10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd < my_best:
                    my_best = myd
                if opd < opp_best:
                    opp_best = opd
                lead = opd - myd
                if lead > lead_best:
                    lead_best = lead
            val = 12 * lead_best - 0.8 * my_best - 0.35 * opp_best - 0.6 * block_pen(nx, ny)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    else:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = -cheb(nx, ny, cx, cy) - 0.6 * block_pen(nx, ny)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]