def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        t = ax - bx
        if t < 0:
            t = -t
        u = ay - by
        if u < 0:
            u = -u
        return t + u

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = None
        opd = None
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs:
                continue
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            score = (d2 - d1) * 100 - d1
            if myd is None or score > bestv:
                pass
            if myd is None:
                myd = d1
                opd = d2
            # maximize advantage; deterministic tie-break by smaller distance to resource
            if score > bestv:
                bestv = score
                best = (dx, dy)
            elif score == bestv and (myd is not None and d1 < myd):
                best = (dx, dy)
                myd = d1
                opd = d2

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]