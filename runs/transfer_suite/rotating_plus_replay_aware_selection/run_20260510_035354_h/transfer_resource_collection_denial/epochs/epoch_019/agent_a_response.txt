def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def move_toward(nx, ny, tx, ty):
        dx = 0 if tx == nx else (1 if tx > nx else -1)
        dy = 0 if ty == ny else (1 if ty > ny else -1)
        return dx, dy

    # Pick best target by "race" advantage: opponent arrival minus my arrival.
    bestcand = None
    tx = ty = resources[0][0], resources[0][1]
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        cand = (opd - myd, -myd, -rx, -ry, rx, ry)
        if bestcand is None or cand > bestcand:
            bestcand = cand
            tx, ty = rx, ry

    # If there is an even more favorable target, occasionally bias toward it.
    # Deterministic: still based on observed race advantage.
    top = []
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        top.append((opd - myd, -myd, -rx, -ry, rx, ry))
    top.sort(reverse=True)
    if len(top) >= 2 and top[1][0] == top[0][0]:
        # choose the one where my distance is smaller (tighter claim) deterministically
        if (-top[1][1]) < (-top[0][1]):
            tx, ty = top[1][4], top[1][5]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Prefer obstacle-safe moves, then best tactical score.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Small tie-break: also consider approach to the best resource set (second-best helps avoid dead-ends).
        second = top[1] if len(top) > 1 else top[0]
        srx, sry = second[4], second[5]
        myd2 = cheb(nx, ny, srx, sry)
        opd2 = cheb(ox, oy, srx, sry)
        cand = ((opd - myd) + 0.25 * (opd2 - myd2), -myd, -myd2, dx, dy)
        if best is None or cand > best:
            best = cand
            bestmove = [dx, dy]

    if best is None:
        # all neighboring invalid -> stay
        return [0, 0]
    return bestmove