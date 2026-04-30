def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not free(start[0], start[1]): return dist
        q = [start]; qi = 0
        dist[start[0]][start[1]] = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if resources:
        best = None
        for rx, ry in resources:
            dme = myd[rx][ry]; dop = opd[rx][ry]
            if dme >= 10**8 or dop >= 10**8:
                continue
            # Prefer winning: larger (dop - dme), then smaller dme, then deterministic coord tie
            key = (dop - dme, -dme, -cheb(sx, sy, rx, ry), -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        if best is not None:
            _, (tx, ty) = best
            cur = myd[sx][sy]
            cand = []
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not free(nx, ny): 
                    continue
                cand.append((myd[nx][ny], cheb(nx, ny, tx, ty), dx, dy))
            # Move that reduces distance to target by our BFS; tie-break by direct closeness then determinism
            cand.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
            if cand:
                _, _, dx, dy = cand[0]
                return [int(dx), int(dy)]

    # No reachable resource: move toward opponent side while avoiding obstacles
    tx, ty = (w - 1, 0) if (sx + sy) <= (ox + oy) else (0, h - 1)
    best = (10**9, 10**9, 0, 0)  # dist to opponent target, cheb to opponent, dx, dy
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        dd = cheb(nx, ny, ox, oy)
        dt = cheb(nx, ny, tx, ty)
        cand = (dt, dd, dx, dy)
        if cand < best:
            best = cand
    return [int(best[2]), int(best[3])]