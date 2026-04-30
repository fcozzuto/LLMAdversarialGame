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
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Pick a target resource: prefer ones we can reach earlier than opponent.
    best_val = -10**18
    target = resources[0]
    for rx, ry in resources:
        my_d = cheb(mx, my, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        val = (op_d - my_d) * 10 - my_d  # bigger means better
        if val > best_val:
            best_val = val
            target = (rx, ry)
        elif val == best_val:
            # deterministic tie: closer to us, then lexicographic
            if my_d < cheb(mx, my, target[0], target[1]) or (my_d == cheb(mx, my, target[0], target[1]) and (rx, ry) < target):
                target = (rx, ry)

    rx, ry = target
    best = (10**9, -10**9, 0, 0)  # (our_dist, -opp_dist, dx, dy)
    for dx, dy in moves:
        nx, ny = mx + dx, my + dy
        if not legal(nx, ny):
            continue
        our_d = cheb(nx, ny, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        score = (our_d, -opp_d)
        cand = (score[0], score[1], dx, dy)
        if cand < best:
            best = cand
    return [best[2], best[3]]