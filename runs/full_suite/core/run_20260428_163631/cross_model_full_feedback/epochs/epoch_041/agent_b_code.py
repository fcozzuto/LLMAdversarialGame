def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
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

    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Target a resource if available, else head toward center to threaten
    if resources:
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = man((sx, sy), (rx, ry))
            if d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            rx, ry = best
            dx = 0 if rx == sx else (1 if rx > sx else -1)
            dy = 0 if ry == sy else (1 if ry > sy else -1)
            cand = (dx, dy)
            if cand in legal:
                return [dx, dy]

    # Fallback: move closer to opponent to apply pressure
    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    if (dx, dy) in legal:
        return [dx, dy]

    # If direct toward opponent blocked, search closest legal move reducing distance to opponent
    bestm = None
    bestd = 10**9
    for dx2, dy2 in legal:
        nx, ny = sx + dx2, sy + dy2
        d = man((nx, ny), (ox, oy))
        if d < bestd:
            bestd = d
            bestm = (dx2, dy2)
    if bestm is not None:
        return [bestm[0], bestm[1]]

    # Last resort stay
    return [0, 0]