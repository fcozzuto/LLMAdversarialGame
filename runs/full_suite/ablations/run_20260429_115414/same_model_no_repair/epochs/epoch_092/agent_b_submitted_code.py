def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inside(start[0], start[1]):
            return dist
        q = [start]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = max(abs(nx - cx), abs(ny - cy))
                if d < best[0]:
                    best = (d, dx, dy)
        return [best[1], best[2]]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best_res = None
    best_adv = -10**18
    best_ds = 10**18
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        myd = ds[rx][ry]
        opd = do[rx][ry]
        if myd >= 10**8 and opd >= 10**8:
            continue
        adv = opd - myd
        if adv > best_adv or (adv == best_adv and myd < best_ds):
            best_adv, best_ds, best_res = adv, myd, (rx, ry)

    if best_res is None:
        return [0, 0]

    rx, ry = best_res

    def dist_to_target_from(xy):
        dist = bfs(xy)
        return dist[rx][ry]

    best = (-10**18, 10**18, 0, 0)  # (adv, myd, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd_next = dist_to_target_from((nx, ny))
        opd = do[rx][ry]
        adv = opd - myd_next
        if myd_next >= 10**8:
            continue
        key = (adv, -myd_next)
        if adv > best[0] or (adv == best[0] and myd_next < best[1]) or (adv == best[0] and myd