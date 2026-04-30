def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    # collect if already on resource
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # choose target resource with best contest advantage
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            advantage = opd - myd  # positive means we are closer
            # if no positive advantage, still pick closest-to-us but discourage very late races
            score = advantage * 10 - myd
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # score each possible move by progress to target and denying opponent
    bestm = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # immediate value: if move onto a resource, take it
        on_res = any(nx == rx and ny == ry for rx, ry in resources)
        if on_res:
            return [dx, dy]
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # prefer reducing our distance while keeping opponent distance large
        score = (opd - myd) * 50 - myd
        # subtle safety: don't run too close if it doesn't help capture
        score -= cheb(nx, ny, ox, oy) * 0.5
        if bestm is None or score > bestm[0]:
            bestm = (score, dx, dy)

    if bestm is None:
        return [0, 0]
    return [bestm[1], bestm[2]]