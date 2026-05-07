def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    if w <= 0 or h <= 0 or not resources:
        return [0, 0]

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(ax, ay, bx, by):
        return max(abs(bx - ax), abs(by - ay))

    def best_resource_value(nx, ny):
        # maximize over resources: prefer guaranteed earlier pickup; otherwise heavily penalize.
        best = (-10**30, None)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nx, ny, rx, ry)
            ot = dist(ox, oy, rx, ry)
            val = 0
            if st < ot:
                # we can race and win
                val = 10**9 + (ot - st) * 10**6 - st * 1000 + (rx + ry)
            elif st == ot:
                # tie: still good but less certain
                val = 5 * 10**8 - st * 2000 + (rx + ry)
            else:
                # opponent likely takes it
                gap = st - ot
                val = -10**7 * gap - st * 10 + (rx + ry) * 0.01
            if val > best[0]:
                best = (val, (rx, ry, st, ot))
            elif val == best[0] and (rx + ry) > (best[1][0] + best[1][1]):
                best = (val, (rx, ry, st, ot))
        return best[0]

    # primary: pick move that maximizes ability to be first on some resource
    best_move = (0, 0)
    best_score = -10**30
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        sc = best_resource_value(nx, ny)

        # secondary: if move doesn't win any resource, reduce giving opponent an uncontested win
        # (estimate by checking whether there exists a resource where opponent is strictly earlier)
        opp_adv = False
        min_gap = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nx, ny, rx, ry)
            ot = dist(ox, oy, rx, ry)
            if ot < st:
                opp_adv = True
                gap = st - ot
                if gap < min_gap:
                    min_gap = gap
        if opp_adv:
            sc -= 2 * (min_gap * 10**4)

        # tertiary deterministic tie-break: move ordering already deterministic; add slight bias toward increasing x then y
        if sc > best_score:
            best_score = sc
            best_move = (mdx, mdy)

    return [best_move[0], best_move[1]]