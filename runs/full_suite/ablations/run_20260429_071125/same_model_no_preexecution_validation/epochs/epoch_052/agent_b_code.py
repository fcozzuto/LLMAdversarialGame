def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_t = None
    best_adv = -INF
    best_ds = INF
    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            adv = 10**6
        else:
            adv = do - ds
        if adv > best_adv or (adv == best_adv and (ds < best_ds or (ds == best_ds and (tx, ty) < best_t))):
            best_adv = adv
            best_ds = ds
            best_t = (tx, ty)

    if best_t is None:
        return [0, 0]

    tx, ty = best_t
    cur_d = distS[sx][sy]
    best_move = (0, 0)
    best_d = distS[sx][sy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = distS[nx][ny]
        if d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    if best_d >= cur_d and (sx, sy) != (tx, ty):
        # If stuck due to tie/edge, still try to reduce distance when possible
        best_move = (0, 0)
        best_d = cur_d
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = distS[nx][ny]
            if d < best_d or (d == best_d and (dx, dy) < best_move):
                best_d = d
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]