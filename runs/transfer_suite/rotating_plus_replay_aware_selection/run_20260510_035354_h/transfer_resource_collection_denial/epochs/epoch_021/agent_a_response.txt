def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    # Pick target where we have best "race" advantage (opponent arrival minus my arrival).
    best = None
    tx, ty = resources[0]
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Secondary: closer target; tertiary: deterministic by coordinates.
        cand = (opd - myd, -myd, -rx, -ry, rx, ry)
        if best is None or cand > best:
            best = cand
            tx, ty = rx, ry

    # Greedy move among up to 8 neighbors that are valid, minimizing distance to target.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # Also prefer not getting "stuck" against obstacles (small penalty for being adjacent to obstacles).
        adj = 0
        for ax, ay in deltas:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obs:
                adj += 1
        candm = (-(dist), -(adj), -dx, -dy, dx, dy)
        if bestm is None or candm > bestm:
            bestm = candm

    if bestm is None:
        return [0, 0]

    # Recover dx,dy from bestm tuple
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        adj = 0
        for ax, ay in deltas:
            px, py = nx + ax, ny + ay
            if 0 <= px < w and 0 <= py < h and (px, py) in obs:
                adj += 1
        candm = (-(dist), -(adj), -dx, -dy, dx, dy)
        if candm == bestm:
            return [dx, dy]

    return [0, 0]