def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(ax, ay, bx, by): 
        return abs(ax - bx) + abs(ay - by)

    def free_neighbors(x, y):
        c = 0
        for dxx, dyy in deltas:
            tx, ty = x + dxx, y + dyy
            if inb(tx, ty) and (tx, ty) not in obstacles:
                c += 1
        return c

    best = None
    best_sc = -10**9
    has_res = len(resources) > 0
    for dx, dy, nx, ny in legal:
        if has_res:
            dmin = 10**9
            for rx, ry in resources:
                d = md(nx, ny, rx, ry)
                if d < dmin: dmin = d
            sc = -dmin * 10 + free_neighbors(nx, ny)
        else:
            d = md(nx, ny, ox, oy)
            sc = -d * 10 + free_neighbors(nx, ny)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [int(best[0]), int(best[1])]