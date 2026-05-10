def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_key = (-10**9, -10**9)
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    def best_step_toward(tx, ty):
        bestm = (0, 0)
        bestk = (-10**9, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            sd2 = cheb(nx, ny, tx, ty)
            od2 = cheb(ox, oy, tx, ty)
            # primary: reduce our distance; secondary: worsen opponent's distance to this resource
            k = (-sd2, od2)
            if k > bestk:
                bestk = k
                bestm = (dx, dy)
        return list(bestm)

    if best is not None:
        return best_step_toward(best[0], best[1])

    # No resources: drift toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    bestm = [0, 0]
    bestd = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = cheb(nx, ny, cx, cy)
        if d < bestd:
            bestd = d
            bestm = [dx, dy]
    return bestm