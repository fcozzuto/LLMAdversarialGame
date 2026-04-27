def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    tx = (w - 1) // 2
    ty = (h - 1) // 2
    if resources:
        best = None
        best_adv = -10**9
        best_dme = 10**9
        for rx, ry in resources:
            dme = cheb(mx, my, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            adv = dop - dme
            if adv > best_adv or (adv == best_adv and dme < best_dme):
                best_adv = adv
                best_dme = dme
                best = (rx, ry)
        if best is not None:
            tx, ty = best

    # Choose one move that gets us closest to (tx,ty); tie-break by increasing opponent distance.
    best_move = (0, 0)
    best_dm = 10**9
    best_do = -10**9
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        dm = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        if dm < best_dm or (dm == best_dm and do > best_do):
            best_dm = dm
            best_do = do
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]