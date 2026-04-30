def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

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
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def best_move_towards(target):
        tdx = target[0] - sx
        tdy = target[1] - sy
        cand = []
        for dx, dy in legal:
            if (dx == 0 and tdx == 0) or (dx != 0 and (dx > 0) == (tdx > 0)):
                if (dy == 0 and tdy == 0) or (dy != 0 and (dy > 0) == (tdy > 0)):
                    cand.append((dx, dy))
        if cand:
            return cand[0]
        return legal[0]

    if resources:
        # target nearest resource, then head to it
        best = None
        bestd = 10**9
        for rx, ry in resources:
            d = man((sx, sy), (rx, ry))
            if d < bestd:
                bestd = d
                best = (rx, ry)
        if best is not None:
            return list(best_move_towards(best))

    # Fallback: approach center to pressure
    center = (w//2, h//2)
    return list(best_move_towards(center))