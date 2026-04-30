def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # choose move that maximizes our advantage to some resource vs opponent
            cur_best = -10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # prioritize resources we can reach sooner; break ties toward smaller ds
                val = (do - ds) * 1000 - ds
                if val > cur_best:
                    cur_best = val
            if cur_best > best_val:
                best_val = cur_best
                best_move = [dx, dy]
        return best_move

    # No visible resources: move toward center while slightly avoiding opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dcent = cheb(nx, ny, cx, cy)
        dmid = cheb(nx, ny, ox, oy)
        val = (-dcent) * 10 + dmid
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move