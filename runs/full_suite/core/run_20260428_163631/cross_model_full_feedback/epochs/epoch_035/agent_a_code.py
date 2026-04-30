def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
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
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        target = resources[0]
        bestd = man((sx, sy), target)
        for t in resources[1:]:
            d = man((sx, sy), t)
            if d < bestd:
                bestd = d
                target = t
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dres = man((nx, ny), target)
            dopp = man((nx, ny), (ox, oy))
            v = -dres * 1000 + dopp
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No resources: maximize distance from opponent.
    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = man((nx, ny), (ox, oy))
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]