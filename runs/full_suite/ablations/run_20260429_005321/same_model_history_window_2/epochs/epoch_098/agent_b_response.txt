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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    opp_dists = {}
    for rx, ry in resources:
        opp_dists[(rx, ry)] = cheb(ox, oy, rx, ry)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if dx == 0 and dy == 0 and (nx, ny) in resources:
            pass
        cur_best = -10**18
        for rx, ry in resources:
            our = cheb(nx, ny, rx, ry)
            opp = opp_dists[(rx, ry)]
            margin = opp - our
            val = margin * 100 - our  # strong preference for resources we can secure earlier
            if (nx, ny) == (rx, ry):
                val += 5000
            if val > cur_best:
                cur_best = val
        # slight deterministic tie-break to keep movement stable: prefer moves that reduce own distance to nearest resource
        nearest_self = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        val_total = cur_best - nearest_self * 0.001
        if val_total > best_val:
            best_val = val_total
            best_move = [dx, dy]

    return best_move