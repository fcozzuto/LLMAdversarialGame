def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Pick target: maximize chance to arrive first (min (dS-dO)), then closer, then ordering.
    best = None
    best_key = None
    for rx, ry in res:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        key = (dS - dO, dS, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dS = cheb(nx, ny, tx, ty)
        # Encourage reducing distance and also staying ahead of opponent on the way to the same target.
        dO = cheb(ox, oy, tx, ty)
        key = (dS, (dS - dO), abs(nx - tx) + abs(ny - ty), nx, ny)
        if bestk is None or key < bestk:
            bestk = key
            bestm = (dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]