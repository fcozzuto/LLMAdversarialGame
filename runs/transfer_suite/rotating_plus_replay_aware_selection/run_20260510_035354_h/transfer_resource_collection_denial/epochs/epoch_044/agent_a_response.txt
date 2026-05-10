def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = int(observation.get("turns_remaining", 0))

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            t = (int(p[0]), int(p[1]))
            if t not in obs:
                res.append(t)
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Strategic tweak: as time dwindles, prioritize secure closest resource;
    # otherwise prioritize denial (maximize opp distance advantage vs self).
    time_weight = 0.85 if turns_remaining <= 8 else 1.0

    best_move = [0, 0]
    best_key = (-10**18, -10**18, -10**18, -10**18)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate this move by best resource for contest/collection.
        best_for_move = (-10**18, -10**18, -10**18, -10**18)
        for tx, ty in res:
            myD = cheb(nx, ny, tx, ty)
            oppD = cheb(ox, oy, tx, ty)
            # Denial score: higher means opponent is farther (or we are closer).
            denial = (oppD - myD) * (1.0 if time_weight >= 0.9 else 0.85)
            # Secure score: prefer smaller myD, also prefer target closer to us than to center only as tie-break.
            secure = -myD
            # Extra tie-break: slight preference for moving toward the "frontier" (toward opponent side).
            frontier = -(cheb(nx, ny, ox, oy))
            # Deterministic composite: compare denial, then secure, then frontier, then stable coordinate.
            key = (denial, secure, frontier, -(tx + ty))
            if key > best_for_move:
                best_for_move = key

        if best_for_move > best_key:
            best_key = best_for_move
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]