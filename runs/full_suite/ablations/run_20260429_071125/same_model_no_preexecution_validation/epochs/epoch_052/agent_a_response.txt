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
    best_mode = 0  # 1 = we are strictly closer, 0 = no advantage; choose nearest
    best_key = None

    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        mode = 1 if do > ds else 0
        if best is None:
            best = (tx, ty)
            best_mode = mode
            best_key = (mode, - (do - ds), ds) if mode == 1 else (mode, ds, -do)
        else:
            if mode > best_mode:
                best = (tx, ty)
                best_mode = mode
                best_key = (mode, - (do - ds), ds) if mode == 1 else (mode, ds, -do)
            elif mode == best_mode:
                key = (mode, - (do - ds), ds) if mode == 1 else (mode, ds, -do)
                if key < best_key:
                    best = (tx, ty)
                    best_key = key

    if best is None:
        return [0, 0]

    tx, ty = best
    if distS[tx][ty] >= INF:
        return [0, 0]

    best_move = (0, 0)
    best_val = INF
    best_tieb = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = distS[nx][ny]
        if d < best_val:
            best_val = d
            best_move = (dx, dy)
            best_tieb = distO[nx][ny]
        elif d == best_val:
            # If equally good for us, prefer moves that are worse for opponent (higher distO).
            if distO[nx][ny] > best_tieb:
                best_move = (dx, dy)
                best_tieb = distO[nx][ny]

    return [int(best_move[0]), int(best_move[1])]