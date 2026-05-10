def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or sp
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def make_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    oppT = make_set("opponent_territory")
    selfT = make_set("self_territory")

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    targets = []
    res = observation.get("resources") or []
    if res:
        for p in res:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    targets.append((x, y))
    if not targets:
        targets = [(ox, oy)]

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        tx, ty = targets[0]
        dmin = md(nx, ny, targets[0][0], targets[0][1])
        for i in range(1, len(targets)):
            t2x, t2y = targets[i]
            d = md(nx, ny, t2x, t2y)
            if d < dmin:
                dmin, tx, ty = d, t2x, t2y
        val = -dmin
        if (nx, ny) in oppT:
            val += 1000
        if (nx, ny) in selfT:
            val += 10
        if (nx, ny) == (ox, oy):
            val += 2000
        if val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]