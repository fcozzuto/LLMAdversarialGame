def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            # Strongly avoid opponent; slightly prefer moving toward our starting corner (0,0) if safe
            v = cheb(nx, ny, ox, oy) * 1000 - (nx * 2 + ny * 2)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Precompute opponent closeness to resources for denial pressure
    min_opp = 10**9
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if d < min_opp:
            min_opp = d

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        # Choose the resource that gives best immediate advantage after this move
        vbest = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Advantage + denial bonus (resources opponent is relatively closest to)
            denial = 0
            if od == min_opp:
                denial = 250
            v = (od - sd) * 40 - sd + denial
            if v > vbest:
                vbest = v

        # Also prefer moves that increase separation from opponent while not sacrificing target value
        vtotal = vbest + cheb(nx, ny, ox, oy) * 3
        if vtotal > bestv or (vtotal == bestv and (dx, dy) < best):
            bestv = vtotal
            best = (dx, dy)

    return [best[0], best[1]]