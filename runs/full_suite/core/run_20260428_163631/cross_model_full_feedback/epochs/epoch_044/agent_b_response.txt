def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
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

    def man(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            d_opp = man((nx, ny), (ox, oy))
            d_res = min(man((nx, ny), r) for r in resources)
            # discourage moving into opponent's immediate grasp
            val = -d_res
            if d_opp <= 1:
                val -= 2
            if best is None or val > bestv:
                best = (dx, dy)
                bestv = val
        if best is not None:
            return [best[0], best[1]]

    # Fallback: move toward center if safe, else toward farthest corner
    center = (w//2, h//2)
    def score_move(dx, dy, nx, ny):
        return - (abs(nx - center[0]) + abs(ny - center[1]))
    best = None
    bestv = None
    for dx, dy, nx, ny in legal:
        s = score_move(dx, dy, nx, ny)
        if best is None or s > bestv:
            best = (dx, dy)
            bestv = s
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]