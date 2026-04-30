def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles", [])
    obs = set(obstacles)

    resources = observation.get("resources", [])
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        best = None
        bestv = None
        for dx, dy, nx, ny in moves:
            # maximize: closer to resources, farther from them for opponent
            v = 0
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                v += (do - ds) * 1.0
            # small tie-break: prefer not staying if equally good
            if v == 0 and dx == 0 and dy == 0:
                v -= 0.01
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # no visible resources: drift toward center while increasing distance from opponent
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    bestv = None
    for dx, dy, nx, ny in moves:
        dc = cheb(nx, ny, cx, cy)
        do = cheb(nx, ny, ox, oy)
        v = do - 0.3 * dc
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)
    return [int(best[0]), int(best[1])]