def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inside(start[0], start[1]):
            return dist
        dist[start[0]][start[1]] = 0
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    if not resources:
        tx, ty = (w // 2, h // 2)
        best = (10**9, 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = abs(nx - tx) + abs(ny - ty)
                if (d, 0) < best:
                    best = (d, 0)
                    bx, by = dx, dy
        return [bx, by] if 'bx' in locals() else [0, 0]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # score next position by best contested advantage among reachable resources
        local_best = -10**18
        for rx, ry in resources:
            d1 = myd[nx][ny] if False else myd[nx][ny]
            if d1 >= 10**9:
                continue
            d2 = opd[rx][ry]  # opponent distance to resource
            myd_res = myd[nx][ny] if (rx, ry) == (nx, ny) else myd[rx][ry]  # if move isn't on resource, use global
            # combine: prefer resources where we beat opponent and are close
            myd_here = myd[rx][ry]
            if myd_here >= 10**9:
                continue
            opp = d2
            adv = (opp - myd_here)
            # bias slightly toward immediate pickup if we step onto it
            pickup = 4.0 if (nx, ny) == (rx, ry) else 0.0
            val = pickup + (2.0 * adv) - (0.15 * myd_here)
            if val > local_best:
                local_best = val
        if local_best > best_score:
            best_score = local_best
            best_move = [dx, dy]

    return best_move