def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target resource that is most favorable vs opponent from current state
    target = None
    best_t = -10**18
    for rx, ry in resources:
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = (do - dm)  # positive means we are closer
        # slight bias to earlier capture and less travel
        score = score * 1000 - dm
        if score > best_t:
            best_t = score
            target = (rx, ry)

    if target is None:
        # No visible resources: maximize distance from opponent, else go center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = -10**18
        best_mv = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_ctr = cheb(nx, ny, cx, cy)
            sc = d_opp * 10 - d_ctr
            if sc > best:
                best = sc
                best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]

    rx, ry = target
    best_sc = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # We want to be closer than opponent; also progress toward target.
        sc = (opp_d - my_d) * 1000 - my_d
        # If we land exactly on the target, win condition typically best.
        if my_d == 0:
            sc += 10**9
        if sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]