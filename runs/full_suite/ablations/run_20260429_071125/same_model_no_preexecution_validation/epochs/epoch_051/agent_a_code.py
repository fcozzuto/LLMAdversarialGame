def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_key = None
    for tx, ty in resources:
        ds = distS[tx][ty]
        do = distO[tx][ty]
        if ds >= INF and do >= INF:
            continue
        # Prefer targets we can reach while opponent can't; otherwise maximize (do - ds), then closeness to us.
        key = (0, 0, 0)
        if ds < INF and do >= INF:
            key = (2, ds, do)
        elif ds < INF and do < INF:
            key = (1, - (do - ds), ds)  # smaller is better
        else:
            key = (0, do, ds)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    curd = distS[sx][sy]
    # Move: choose neighbor that most reduces our distance to target; if tied, keep opponent distance large; deterministic tie-break.
    best_move = (0, 0)
    best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        # prioritize decreasing our path length; then prefer increasing opponent distance to this target; then prefer straight-ish moves.
        opp_dist = distO[tx][ty]
        opp_here = distO[nx][ny]
        # tie: smaller (nds-curd) is better, larger opp_here is better.
        tie = (nds - curd, -opp_here, abs(dx) + abs(dy), dx, dy)
        if best_tie is None or tie < best_tie:
            best_tie = tie
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]