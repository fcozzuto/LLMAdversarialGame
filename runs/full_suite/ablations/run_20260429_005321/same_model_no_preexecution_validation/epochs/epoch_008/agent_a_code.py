def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    legal = [(dx, dy) for dx, dy in dirs
             if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = ((nx - cx) ** 2 + (ny - cy) ** 2) * -1
            # softly keep away from opponent
            v += ((nx - ox) ** 2 + (ny - oy) ** 2) * 0.05
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))
    resource_set = set((r[0], r[1]) for r in resources)

    # Choose a resource where we have the biggest time advantage; break ties by quicker arrival.
    best_target = None
    best_adv = -INF
    best_our = INF
    for rx, ry in resource_set:
        d1 = our_dist[ry][rx]; d2 = opp_dist[ry][rx]
        if d1 >= INF or d2 >= INF:
            continue
        adv = d2 - d1
        if adv > best_adv or (adv == best_adv and d1 < best_our):
            best_adv = adv; best_our = d1; best_target = (rx, ry)

    # If somehow no reachable resource, just move toward center while avoiding opponent.
    if best_target is None:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None; bestv = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -((nx - cx) ** 2 + (ny - cy) ** 2)
            v += ((nx - ox) ** 2 + (ny -