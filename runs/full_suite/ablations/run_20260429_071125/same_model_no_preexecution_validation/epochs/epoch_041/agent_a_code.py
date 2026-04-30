def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if (sx, sy) in resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        if do >= INF:
            do = INF
        score = (do - ds)  # larger means we're sooner than opponent
        if score > best_score or (score == best_score and (best is None or (ds, rx, ry) < (distS[best[0]][best[1]], best[0], best[1]))):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best

    def cheb(x, y): 
        ax = x - tx; ay = y - ty
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        dtar = cheb(nx, ny)
        dopp = cheb(nx, ny)  # placeholder to keep deterministic tie ordering
        # better opponent distance (maximize), use chebyshev to opponent
        ax = nx - ox; ay = ny - oy
        if ax <