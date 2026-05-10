def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    res_raw = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    res = [(p[0], p[1]) for p in res_raw if p and len(p) >= 2]
    obs = set((p[0], p[1]) for p in obs_raw if p and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not res:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_target = None
    best_score = -10**18
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Favor resources I can reach significantly earlier; slight preference for being closer overall.
        score = (opd - myd) * 10 - myd
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        myd = cheb(nx, ny, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Keep improving my progress while not letting opponent gain too much.
        val = (opd - myd) * 10 - myd
        # Small deterministic tie-break: move that gets closer in x, then y.
        if nx != rx:
            val -= abs(nx - rx) * 0.01
        if ny != ry:
            val -= abs(ny - ry) * 0.001
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move