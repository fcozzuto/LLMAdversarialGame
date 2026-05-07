def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set(tuple(p) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if resources:
        def cheb(ax, ay, bx, by):
            return max(abs(ax - bx), abs(ay - by))

        # Pick a resource where we can arrive earlier (or at least not later).
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: maximize slack (opp earlier by us)
            key = (opd - myd, -myd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No visible resources: drift toward opponent in a way that keeps options open.
        tx, ty = ox, oy

    def step_toward(tx, ty):
        # Evaluate each legal move by (1) improved distance to target, (2) improved slack vs opponent.
        def dist_after(dx, dy):
            nx, ny = sx + dx, sy + dy
            myd = max(abs(nx - tx), abs(ny - ty))
            opd = max(abs(nx - ox), abs(ny - oy))
            return myd, opd

        bestm = None
        bestk = None
        for dx, dy in legal:
            ndx, odx = dist_after(dx, dy)
            # Lower my distance is good; also prefer reducing opponent distance while approaching target.
            k = (ndx, odx, dx, dy)
            if bestk is None or k < bestk:
                bestk = k
                bestm = (dx, dy)
        return bestm

    md = step_toward(tx, ty)
    if md is None:
        return [0, 0]
    return [md[0], md[1]]