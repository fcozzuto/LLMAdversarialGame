def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_dist(start):
        x0, y0 = start
        if (x0, y0) in obs:
            return {}
        dist = {(x0, y0): 0}
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[(x, y)] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and (nx, ny) not in dist:
                    dist[(nx, ny)] = nd
                    q.append((nx, ny))
        return dist

    opp_dist = bfs_dist((ox, oy))
    INF = 10**9

    best = None
    best_key = None
    for dxm, dym in dirs8:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            my_best_adv = -INF
            my_best_myd = INF
        else:
            my_dist = bfs_dist((nx, ny))
            my_best_adv = -INF
            my_best_myd = INF
            for rx, ry in resources:
                myd = my_dist.get((rx, ry), INF)
                if myd >= INF:
                    continue
                opd = opp_dist.get((rx, ry), INF)
                if opd >= INF:
                    opd = INF
                adv = opd - myd
                if adv > my_best_adv or (adv == my_best_adv and myd < my_best_myd):
                    my_best_adv = adv
                    my_best_myd = myd

        # Primary: maximize advantage; Secondary: minimize my distance to a resource; Tertiary: deterministic move order
        move_key = (my_best_adv, -my_best_myd)
        if best_key is None or move_key > best_key:
            best_key = move_key
            best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]