def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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

    if resources:
        best = None
        bestd = 10**9
        for r in resources:
            d = man((sx, sy), r)
            if d < bestd:
                bestd = d
                best = r
        if best is not None:
            dx = int(best[0] - sx)
            dy = int(best[1] - sy)
            if (dx, dy) in legal:
                return [dx, dy]

    # Move toward opponent if safe, else stay or sidestep deterministically
    ox_t, oy_t = ox, oy
    dx = 0 if ox_t == sx else (1 if ox_t > sx else -1)
    dy = 0 if oy_t == sy else (1 if oy_t > sy else -1)
    # Try primary dx,dy; if blocked, try other legal moves in a fixed order
    cand = [(dx, dy), (0, dy), (dx, 0), (1,1), (-1,-1), (1,-1), (-1,1), (1,0), (0,1), (-1,0)]
    for mx, my in cand:
        if (mx, my) in legal:
            return [mx, my]
    # Fallback to any legal
    if legal:
        return [legal[0][0], legal[0][1]]
    return [0, 0]