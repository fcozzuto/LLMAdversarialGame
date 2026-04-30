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

    if resources:
        # deterministic: pick nearest resource, break ties by x then y
        best = None
        bestd = 10**9
        for r in resources:
            d = man((sx, sy), r)
            if d < bestd or (d == bestd and (r < best)):
                bestd = d
                best = r
        # move towards best if possible in one step
        if best is not None:
            dx = 0 if best[0] == sx else (1 if best[0] > sx else -1)
            dy = 0 if best[1] == sy else (1 if best[1] > sy else -1)
            nd = (dx, dy)
            if nd in legal:
                return [dx, dy]
            # if cannot move directly, try composite toward resource via closest legal step
            # pick legal step that minimizes distance to resource
            best_step = None
            best_d = 10**9
            for lx, ly in legal:
                tx, ty = sx + lx, sy + ly
                d = man((tx, ty), best)
                if d < best_d:
                    best_d = d
                    best_step = (lx, ly)
            if best_step is not None:
                return [best_step[0], best_step[1]]

    # If no reachable resource or not favorable, move toward opponent to contest, deterministically
    # choose legal move that reduces Manhattan distance to opponent
    best_step = None
    best_d = 10**9
    for lx, ly in legal:
        tx, ty = sx + lx, sy + ly
        d = man((tx, ty), (ox, oy))
        if d < best_d:
            best_d = d
            best_step = (lx, ly)
    if best_step is not None:
        return [best_step[0], best_step[1]]

    # Fallback
    return [0, 0]