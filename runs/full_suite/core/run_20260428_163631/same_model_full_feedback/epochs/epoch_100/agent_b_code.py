def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick best target: primarily maximize my advantage in race, then prefer earlier capture.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive if I'm closer
        center_bias = -((rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2)
        # If we're behind, still sometimes chase if it is much earlier for us than it is for opponent.
        key = (adv, -myd, center_bias, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Optional interception: if opponent is extremely close to any resource and I'm close enough to contest,
    # switch to the most "stealable" one (highest adv among resources where opponent is adjacent/near).
    opp_close = []
    for rx, ry in resources:
        opd = cheb(ox, oy, rx, ry)
        if opd <= 2:
            myd = cheb(sx, sy, rx, ry)
            opp_close.append(((opd - myd), -myd, -rx, -ry, (rx, ry)))
    if opp_close:
        opp_close.sort(reverse=True)
        cand = opp_close[0]
        if cand[0] >= 0:  # I'm not worse; contest
            tx, ty = cand[4]

    # Move one step to reduce Chebyshev distance to target, avoiding obstacles.
    best_step = [0, 0]
    best_dist = None
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # small tie-breaker: move toward target direction, and avoid drifting away from target.
                tie = -(abs((tx - nx)) + abs((ty - ny)))
                candidates.append((d, tie, dx, dy))
    candidates.sort(key=lambda t: (t[0], -t[1], abs(t[2]) + abs(t[3])))
    if candidates:
        _, _, dx, dy = candidates[0]
        best_step = [int(dx), int(dy)]
    return best_step