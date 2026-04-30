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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    res_sorted = sorted(resources, key=lambda r: (r[0] - sx) * (r[0] - sx) + (r[1] - sy) * (r[1] - sy))
    keep = res_sorted[:6]
    best = [0, 0]
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)
        d_res = min(cheb(nx, ny, rx, ry) for rx, ry in keep)
        d_res_opp = min(cheb(ox, oy, rx, ry) for rx, ry in keep)
        v = (-d_res) + 0.20 * d_op + 0.45 * (d_res_opp - d_res)
        if (nx, ny) in resources:
            v += 5.0
        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv and [dx, dy] < best:
            best = [dx, dy]

    return best