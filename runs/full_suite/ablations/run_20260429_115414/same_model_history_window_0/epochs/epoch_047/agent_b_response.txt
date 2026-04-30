def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [7, 7])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        dself = cheb(sx, sy, rx, ry)
        dopp = cheb(ox, oy, rx, ry)
        val = (dopp - dself) * 100 - dself
        key = (-val, dself, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        opp_dist = cheb(nx, ny, ox, oy)
        # Prefer moves that advance to target; break ties by safer/less contested positions.
        score = (dist * 1000) - opp_dist
        # Stronger preference for exact contact with the target.
        if (nx, ny) == (tx, ty):
            score -= 100000
        # Add slight deterministic bias to reduce oscillations: favor staying if equally good.
        if (dx, dy) == (0, 0):
            score -= 3
        scored.append((score, dist, -opp_dist, dx, dy))
    if not scored:
        return [0, 0]
    scored.sort()
    return [scored[0][3], scored[0][4]]