def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    if not res:
        bestdx, bestdy = 0, 0
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                bestdx, bestdy = dx, dy
        return [int(bestdx), int(bestdy)]

    t = int(observation.get("turn_index", 0) or 0)
    parity_bias = 1 if (t % 2 == 0) else -1

    # Choose target resource: prefer ones we can reach sooner than opponent.
    target = None
    bestt = -10**18
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # tie-break toward safer/central-ish tiles
        center = (rx - (w - 1) / 2) ** 2 + (ry - (h - 1) / 2) ** 2
        v = (do - ds) * 1000 - ds * 3 + (parity_bias * ((rx + ry) & 1)) - center * 0.01
        if v > bestt:
            bestt = v
            target = (rx, ry)

    tx, ty = target
    bestv = -10**18
    bestdx, bestdy = 0, 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        # Try to seize target faster, while discouraging proximity to opponent.
        v = -ds2 * 1000 + do2 * 5 + (parity_bias * (((nx + ny) & 1) - ((sx + sy) & 1)))
        if v > bestv:
            bestv = v
            bestdx, bestdy = dx, dy

    return [int(bestdx), int(bestdy)]