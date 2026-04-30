def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Choose a target you can reach earlier; otherwise minimize your distance.
    best = None
    best_score = None
    for tx, ty in resources:
        ds, do = distS[tx][ty], distO[tx][ty]
        if ds >= INF: 
            continue
        # Primary: advantage ds<do (or equal), Secondary: speed, Tertiary: deterministic target ordering.
        adv = (do - ds)  # larger is better
        block_pen = 0
        if (tx, ty) in obstacles: block_pen = -1000
        score = (1 if adv >= 0 else 0, adv, -ds, -(tx * 10 + ty))  # lexicographic
        # Compare as deterministic "max" on tuples
        if best is None or score > best_score:
            best = (tx, ty)
            best_score = score

    if best is None:
        return [0, 0]

    tx, ty = best
    # Move one step to keep shortest-path progress; tie-break by maximizing (your distance advantage).
    curd = distS[sx][sy]
    best_move = (0, 0)
    best_md = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        if distS[nx][ny] >= curd:  # must progress (or stay if target is current)
            if (nx, ny) != (tx, ty): 
                continue
        # Prefer neighbor that decreases your distance to target; if tie, prefer higher advantage vs opponent.
        my_step = distS[nx][ny] - distS[tx][ty]
        # Equivalent to preferring smaller dist to target; represent as negative.
        md = -(distS[nx][ny]) + (distO[nx][ny] - distS[nx][ny])
        if md > best_md:
            best_md = md
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]