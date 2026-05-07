def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]

    if (sx, sy) in res:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    opp_adj = False
    for r in res:
        if md((ox, oy), r) <= 1:
            opp_adj = True
            break

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    best_move = None
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # pick target that maximizes advantage from next position
        best_r = None
        best_r_val = None
        for r in res:
            myd = md((nx, ny), r)
            opd = md((ox, oy), r)
            # want myd <= opd; also slight preference for closer resources
            val = (opd - myd, -(myd), r[0], r[1])
            if best_r_val is None or val > best_r_val:
                best_r_val = val
                best_r = r
        # if opponent is about to collect something, emphasize immediate contesting
        target = best_r
        myd = md((nx, ny), target)
        opd = md((ox, oy), target)
        v = (opd - myd, -myd, -0 if (nx, ny) == target else 1, dx, dy)
        if opp_adj:
            # strengthen by also considering the "second-best" resource quickly
            # (only adds constant work)
            second = None
            second_val = None
            for r in res:
                if r == target:
                    continue
                myd2 = md((nx, ny), r)
                opd2 = md((ox, oy), r)
                val2 = (opd2 - myd2, -myd2, r[0], r[1])
                if second_val is None or val2 > second_val:
                    second_val = val2
                    second = r
            if second is not None:
                myd2 = md((nx, ny), second)
                opd2 = md((ox, oy), second)
                v = (min(opd - myd, opd2 - myd2), -min(myd, myd2), v[2], v[3], v[4])

        if best_val is None or v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]