def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = set()
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_dx, best_dy = 0, 0
    best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = 0
        if (nx, ny) in resources:
            val += 10000
        if resources:
            myd = 10**9
            opd = 10**9
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                if d1 < myd: myd = d1
                d2 = cheb(ox, oy, rx, ry)
                if d2 < opd: opd = d2
            if myd < 10**9 and opd < 10**9:
                val += (opd - myd) * 200
        val -= cheb(nx, ny, ox, oy) * 3
        if val > best:
            best = val
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]