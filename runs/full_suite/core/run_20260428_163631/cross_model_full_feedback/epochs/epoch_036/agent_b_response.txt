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
            if inb(x, y): obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst: resources.append((x, y))
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

    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If a resource is adjacent or on current cell, try to move toward it if reachable now
    if resources:
        best = None
        bestd = 10**9
        for r in resources:
            d = man((sx, sy), r)
            if d < bestd:
                bestd = d
                best = r
        if best is not None and bestd <= 1:
            dx = best[0] - sx
            dy = best[1] - sy
            if (dx, dy) in legal:
                return [dx, dy]

    # Otherwise move to maximize distance from opponent while staying as central as possible
    best_move = None
    best_score = -10**9
    cx, cy = w//2, h//2

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # distance to opponent
        od = abs(nx - ox) + abs(ny - oy)
        # distance to center (to encourage balanced play)
        cd = abs(nx - cx) + abs(ny - cy)
        score = od * 2 - cd
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is not None:
        return [best_move[0], best_move[1]]

    return [0, 0]