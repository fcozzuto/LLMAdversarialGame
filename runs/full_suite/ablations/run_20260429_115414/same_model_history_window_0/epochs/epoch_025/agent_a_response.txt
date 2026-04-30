def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    w = observation["grid_width"]
    h = observation["grid_height"]

    # Choose a target resource: maximize (opponent_dist - my_dist), then minimize my_dist
    best_t = None
    best_adv = -10**9
    best_my = 10**9
    for rx, ry in resources:
        myd = cheb(x, y, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and (myd < best_my)):
            best_adv = adv
            best_my = myd
            best_t = (rx, ry)

    # If no resources, head toward opponent corner deterministically
    if best_t is None:
        tx, ty = 7, 7  # opposite corners assumption; if already there, will stay
    else:
        tx, ty = best_t

    # Evaluate candidate moves
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    def eval_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**6
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Strongly prefer moves that reduce my distance to target, but only if I'm competitive
        adv = opd - myd
        # Also mild avoidance of moving toward opponent (to prevent losing contest)
        oppd = cheb(nx, ny, ox, oy)
        return (1000 * adv) - myd + 0.1 * oppd

    best = None
    bestv = -10**18
    for dx, dy, nx, ny in moves:
        v = eval_move(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    # If blocked equally badly, fall back to staying
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]