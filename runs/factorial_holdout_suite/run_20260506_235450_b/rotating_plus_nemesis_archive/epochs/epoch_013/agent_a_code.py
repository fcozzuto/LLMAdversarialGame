def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -(manh(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Greedy competitive advantage: how much closer we are than opponent to the nearest resource.
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = None
        opd = None
        for rx, ry in resources:
            d1 = manh(nx, ny, rx, ry)
            if myd is None or d1 < myd:
                myd = d1
            d2 = manh(ox, oy, rx, ry)
            if opd is None or d2 < opd:
                opd = d2
        # If we can reduce our nearest-resource distance more than theirs, prioritize it.
        adv = (opd - myd)
        # Tie-break: prefer closer to resources overall; slight preference to stay away from edges not needed but helps determinism.
        edge = abs((nx - (w - 1) / 2)) + abs((ny - (h - 1) / 2))
        v = adv * 1000 - myd * 3 - edge * 0.001
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best