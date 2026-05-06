def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obstacle_set = {(a, b) for a, b in obstacles}

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacle_set

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            # When no resources, drift to increase distance from opponent while staying safe-ish
            v = cheb(nx, ny, ox, oy) * 100 - (abs(nx - (w - 1)) + abs(ny - (h - 1)))
            if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
                bestv = v
                best = [dx, dy]
        return best

    # Pick a target resource: prioritize where we are relatively closer than opponent
    best_t = resources[0]
    best_s = -10**18
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # primary: how much closer we are than opponent; secondary: absolute closeness
        s = (od - sd) * 1000 - sd
        if s > best_s:
            best_s = s
            best_t = [rx, ry]

    tx, ty = best_t

    # Choose one step that reduces distance to target, avoids obstacles, and (if tied) contests opponent
    best = [0, 0]
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        os = cheb(nx, ny, ox, oy)
        v = -ns * 1000 + os
        # small tie-breaker: prefer movement that tends to center to reduce edge-sticking
        v -= (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best