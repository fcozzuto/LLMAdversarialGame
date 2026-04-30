def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obst.add((px, py))
        except:
            pass

    res = []
    for r in observation.get("resources", []) or []:
        try:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obst:
                res.append((rx, ry))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a; bx, by = b
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None
    best_score = None

    if res:
        bestd = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = min(cheb((nx, ny), r) for r in res)
            if best_score is None or d > best_score:
                best_score = d
                best = (dx, dy)
    else:
        # Move toward opponent if no resources
        tgtx, tgty = ox, oy
        best = None
        bestd = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = max(abs(nx - tgtx), abs(ny - tgty))  # Chebyshev distance
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]