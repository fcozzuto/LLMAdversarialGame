def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set()
    for p in obstacles_raw:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not resources:
        best = [0, 0]
        bestv = -10**18
        for dx, dy in neigh:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if cheb(nx, ny, ox, oy) <= 1:
                v -= 1
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Choose a contestable target: prioritize resources we are closer to than opponent.
    contenders = []
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        if dS <= dO:
            contenders.append((dO - dS, -dS, rx, ry))  # larger gap first, then closer to us
    if contenders:
        contenders.sort(reverse=True)
        _, _, tx, ty = contenders[0]
    else:
        # If we can't win any nearby, go for the resource where opponent is comparatively worst.
        worsts = []
        for rx, ry in resources:
            dS = cheb(sx, sy, rx, ry)
            dO = cheb(ox, oy, rx, ry)
            worsts.append((dS - dO, dS, rx, ry))  # smaller advantage to opponent is better
        worsts.sort()
        _, _, tx, ty = worsts[0]

    # One-step greedy towards target, with a small anti-collision term vs opponent.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dT = cheb(nx, ny, tx, ty)
        dO = cheb(nx, ny, ox, oy)
        v = -dT
        if dO <= 1:
            v -= 2.0  # avoid letting opponent get adjacent control
        # prefer staying on/off-diagonal slightly to reduce dithering
        if dx == 0 or dy == 0:
            v -= 0.05
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best