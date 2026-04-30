def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))
        except:
            pass

    res = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                res.append((x, y))
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

    def d(a, b, c, e):
        ax = a - c; 
        if ax < 0: ax = -ax
        ay = b - e
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best = legal[0]
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if res:
            ds = 10**9
            do = 10**9
            for rx, ry in res:
                t = d(nx, ny, rx, ry)
                if t < ds: ds = t
                u = d(ox, oy, rx, ry)
                if u < do: do = u
            # Prefer getting closer; strongly prefer positions where opponent is not closer.
            v = -(ds * 20) + (do * 8)
            # Small tie-break: keep distance from opponent to reduce contest odds.
            v += d(nx, ny, ox, oy)
        else:
            v = d(nx, ny, ox, oy)  # maximize separation
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]