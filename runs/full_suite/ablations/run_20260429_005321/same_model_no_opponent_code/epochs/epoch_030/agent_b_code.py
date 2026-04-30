def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            # Prefer moves that get closer to the best "contestable" resource.
            best_res = None
            for rx, ry in resources:
                myd = dist(nx, ny, rx, ry)
                opd = dist(ox, oy, rx, ry)
                # contest if we are not far behind; small myd preferred, then lead.
                score = (myd - opd, myd, rx, ry)
                if best_res is None or score < best_res:
                    best_res = score
            if best is None or best_res < best:
                best = best_res
                chosen = (dx, dy)
        return [int(chosen[0]), int(chosen[1])]

    # No resources: move toward the opponent (to enable capturing/contesting later).
    dx0 = 0
    if ox > x:
        dx0 = 1
    elif ox < x:
        dx0 = -1
    dy0 = 0
    if oy > y:
        dy0 = 1
    elif oy < y:
        dy0 = -1
    # Choose the legal move that most reduces Chebyshev distance to opponent.
    bestd = None
    bestm = (0, 0)
    for dx, dy, nx, ny in legal:
        d = dist(nx, ny, ox, oy)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) == (dx0, dy0)):
            bestd = d
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]