def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    rset = set()
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
                rset.add((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    me = (sx, sy)
    opp = (ox, oy)

    # If no resources, just move to maximize distance from opponent.
    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = dist((nx, ny), opp) - dist(opp, me) * 0.01
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        new = (nx, ny)

        adj_opp = 1 if max(abs(nx - ox), abs(ny - oy)) <= 1 else 0
        on_res = 1 if new in rset else 0

        # Target the resource that gives the strongest advantage (reach earlier).
        best_win = 10**18
        for r in resources:
            my = dist(new, r)
            ot = dist(opp, r)
            win = my - ot  # smaller is better; negative means we are ahead
            if win < best_win:
                best_win = win

        # Score: capture immediate resources strongly; otherwise, prefer negative win.
        v = 0
        v += on_res * 50
        v += (10 if best_win < 0 else 0)
        v += -best_win * 3

        # Reduce getting stuck next to opponent unless we're already ahead.
        if adj_opp:
            v -= 4 if best_win >= 0 else 1

        # Small tie-break: keep moving generally toward the "most winnable" resource.
        v += -dist(new, resources[0]) * 0.01

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best else [0, 0]