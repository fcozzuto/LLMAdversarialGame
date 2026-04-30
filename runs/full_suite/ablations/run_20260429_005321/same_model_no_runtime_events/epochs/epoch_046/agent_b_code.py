def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            cand.append((dx, dy))

    if not cand:
        return [0, 0]

    if resources:
        resources.sort()
        best = None
        bestv = -10**18
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            smin = 10**9
            for tx, ty in resources[:8]:
                d = cheb(nx, ny, tx, ty)
                if d < smin:
                    smin = d
            omin = 10**9
            for tx, ty in resources[:8]:
                d = cheb(ox, oy, tx, ty)
                if d < omin:
                    omin = d
            v = (omin - smin) * 10 - smin
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: head toward opponent while avoiding obstacles
    tx, ty = ox, oy
    best = None
    bestv = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        v = -cheb(nx, ny, tx, ty)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]