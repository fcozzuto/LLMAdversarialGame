def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    if resources:
        best = None
        bestv = -10**18
        for rx, ry in resources:
            d_me = man(sx, sy, rx, ry)
            d_op = man(ox, oy, rx, ry)
            v = (d_op - d_me) * 10 - (rx * rx + ry * ry) * 0.00001
            if v > bestv:
                bestv = v
                best = (rx, ry)
        target = best

    if target is None:
        tx, ty = ox, oy
    else:
        tx, ty = target

    bestmove = (0, 0)
    bestscore = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if resources:
            mind = 10**9
            for rx, ry in resources:
                d = man(nx, ny, rx, ry)
                if d < mind:
                    mind = d
            score = -mind * 10
        else:
            score = -man(nx, ny, tx, ty) * 10
        score += man(ox, oy, nx, ny) * 0.2
        if score > bestscore:
            bestscore = score
            bestmove = (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]