def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if inb(x, y): obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    def obs_risk(x, y):
        # higher risk near obstacles
        r = 0
        for ax in (x-1, x, x+1):
            for ay in (y-1, y, y+1):
                if (ax, ay) in obstacles: r += 1
        return r

    # If there are resources, choose the one where we can reach first (or at least improve),
    # then evaluate moves by progress plus denial (stay away if opponent is closer).
    if resources:
        best_res = None
        best_priority = -10**18
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            # prioritize resources where I'm closer; if none, prioritize closest contested point
            pr = (opd - myd) * 100 - myd
            best_priority = pr if pr > best_priority else best_priority
            if pr == best_priority and best_res is None:
                best_res = (rx, ry)
            if pr > best_priority:
                best_res = (rx, ry)
        rx, ry = best_res
        my0 = md(sx, sy, rx, ry)
        opp0 = md(ox, oy, rx, ry)
        i_am_closer = my0 <= opp0

        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            myd = md(nx, ny, rx, ry)
            opd = md(nx, ny, ox, oy)
            progress = (my0 - myd)
            # denial pressure: if opponent currently closer, maximize distance from opponent
            deny = (opd) * (3 if (not i_am_closer and opp0 < my0) else 1)
            risk = -4 * obs_risk(nx, ny)
            # encourage not overshooting by slight bias toward reducing myd
            approach = -myd * 1.0
            v = progress * 10 + deny + risk + approach
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # No visible resources: move to maximize distance from opponent while avoiding obstacle-adjacent squares
    best = (0, 0)
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        v = md(nx, ny, ox, oy) * 10 - 4 * obs_risk(nx, ny) - (md(nx, ny, 0, 0) + md(nx, ny, w-1, h-1)) * 0.01
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]