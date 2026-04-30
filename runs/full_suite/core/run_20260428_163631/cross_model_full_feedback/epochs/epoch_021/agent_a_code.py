def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obstacles.add((px, py))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not resources:
        best = None
        for dx, dy, nx, ny in legal:
            v = (cheb(nx, ny, ox, oy), dx, dy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    resources.sort()
    best_res = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    best = None
    for dx, dy, nx, ny in legal:
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (abs(ds - do), ds, -ds + do, dx, dy)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]