def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for dx in (-1, 0, 1):
            nx = x + dx
            if nx < 0 or nx >= w: 
                continue
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ny = y + dy
                if 0 <= ny < h and (nx, ny) in obstacles:
                    c += 1
        return c

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target: prefer close to us, far from opponent, and not too obstacle-adjacent.
    best = None
    bestv = 10**9
    for rx, ry in resources:
        v = cheb(sx, sy, rx, ry) - 0.75 * cheb(ox, oy, rx, ry) + 0.25 * adj_obst(rx, ry)
        if v < bestv:
            bestv = v
            best = (rx, ry)
    tx, ty = best

    # If we can take the target now (on it), stay; otherwise move to reduce cost.
    if sx == tx and sy == ty:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    bestm = (0, 0)
    bestc = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Cost: go toward target, avoid obstacles, and slightly spread from opponent if contesting.
        c = cheb(nx, ny, tx, ty) + 0.55 * adj_obst(nx, ny)
        # Contest pressure: if opponent is closer to the target, prioritize faster capture.
        if cheb(ox, oy, tx, ty) <= cheb(sx, sy, tx, ty):
            c -= 0.25 * cheb(nx, ny, tx, ty)
        bestd = cheb(nx, ny, ox, oy)
        c += 0.05 * bestd
        if c < bestc:
            bestc = c