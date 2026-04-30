def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Pick a resource we can reach first, favoring largest distance advantage.
    best = None  # (adv, -dm, rx, ry)
    for rx, ry in resources:
        dm = myd[ry][rx]
        do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        adv = do - dm
        key = (adv, -dm, rx, ry)
        if best is None or key > best:
            best = key

    if best is None:
        # Fallback: move to reduce manhattan distance to nearest resource.
        tx, ty = min(resources, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        bestm = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = abs(nx - tx) + abs(ny - ty)
                od = abs(nx - ox) + abs(ny - oy)
                key = (-d, od)
                if bestm is None or key > bestm:
                    bestm = key
                    bd = (dx, dy)
        return list(bd) if bestm is not None else [0, 0]

    _, _, tx, ty = best

    # Choose the move that best progresses toward target, while considering opponent distance.
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        dm = myd[ny][nx]
        do = opd[ny][nx]
        key = (-(dm if dm < INF else INF), (do if do < INF else -INF))
        if bestd is None or key > bestd:
            bestd = key
            ans = (dx, dy)

    return [int(ans[0]), int(ans[1])] if bestd is not None else [0, 0]