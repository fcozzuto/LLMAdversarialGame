def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if resources:
        best = None
        bestd = 10**18
        bestod = -1
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            od = cheb(nx, ny, ox, oy)
            val = (d, -od)
            if best is None or val < (bestd, bestod):
                best = (dx, dy)
                bestd, bestod = d, -od
        if best is not None:
            return [int(best[0]), int(best[1])]

    # fallback: move toward center while avoiding opponent when possible
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = (0, 0)
    best_key = (10**18, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dc = cheb(nx, ny, cx, cy)
        do = cheb(nx, ny, ox, oy)
        key = (dc, -do)
        if key < best_key:
            best_key = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]