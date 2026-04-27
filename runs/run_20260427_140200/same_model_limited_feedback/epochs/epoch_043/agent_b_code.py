def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            dO = cheb(nx, ny, ox, oy)
            if dO < best[0]:
                best = (dO, 0, dx, dy)
        return [best[2], best[3]]

    # Select a target that I can reach competitively (my advantage over opponent).
    best_target = None
    best_adv = -10**9
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        # small tie-break: prefer nearer resources
        score = adv * 10 - myd
        if score > best_adv:
            best_adv = score
            best_target = (rx, ry)

    rx, ry = best_target
    myd = cheb(sx, sy, rx, ry)
    opd = cheb(ox, oy, rx, ry)

    # If opponent is significantly closer, switch to harassment toward opponent while still moving.
    harass = (opd - myd >= 2)

    best_move = None
    best_val = (10**9, -10**9, 10**9)  # lexicographic
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dT = cheb(nx, ny, rx, ry)
        dO = cheb(nx, ny, ox, oy)
        # First priority: reduce distance to target (or to opponent if harassing)
        if harass:
            primary = dO
            secondary = -dT  # still keep moving toward target
        else:
            primary = dT
            secondary = (dT - cheb(ox, oy, rx, ry))  # lower is better
        # Additional: avoid landing on squares adjacent to opponent (reduce immediate contest)
        adjO = 1 if cheb(nx, ny, ox, oy) == 1 else 0
        val = (primary + adjO * 2, secondary, dO)
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]