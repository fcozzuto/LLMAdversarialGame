def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y): obst.add((x, y))
        except: 
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst: resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obst]
    if not legal: 
        return [0, 0]

    def manh(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    opp = (ox, oy)
    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        me = (nx, ny)
        # If resources exist, prefer those we can reach no later than opponent; otherwise drift to maximize separation.
        if resources:
            dmin = 10**9
            dopp = 10**9
            for rx, ry in resources:
                rr = (rx, ry)
                d1 = manh(me, rr)
                d2 = manh(opp, rr)
                if d1 < dmin: dmin = d1
                if d2 < dopp: dopp = d2
            # Encourage getting closer to nearest resource; discourage opponent being closer to same region.
            # Cheaper reach control term uses nearest resource.
            v = -2 * dmin + (dopp - dmin)
        else:
            v = manh(me, opp)  # maximize distance when no resources
        # Tie-break deterministically toward staying (0,0), then smaller dx, then smaller dy
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]