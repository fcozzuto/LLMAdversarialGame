def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obs = set((x, y) for x, y in obstacles)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    tr = int(observation.get("turns_remaining", 0))
    best = None
    bestk = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # bigger is better
        # Prefer resources we can reach soon; penalize if not.
        miss = 0 if tr >= myd else (myd - tr + 1) * 10
        key = (-adv, miss, myd, rx, ry)
        if bestk is None or key < bestk:
            bestk = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestmk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        step = (dx * dx + dy * dy)
        key = (myd2, step, nx, ny)
        if bestmk is None or key < bestmk:
            bestmk = key
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]