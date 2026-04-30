def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and distS[nx][ny] < bestd:
                bestd = distS[nx][ny]
                best = (dx, dy)
        if valid(tx, ty):
            # move greedily toward center if possible
            dx = 0 if sx == tx else (1 if sx < tx else -1)
            dy = 0 if sy == ty else (1 if sy < ty else -1)
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [best[0], best[1]]

    best_t = None
    best_val = -10**18
    for tx, ty in resources:
        ds = distS[tx][ty]
        do = distO[tx][ty]
        if ds >= INF:
            continue
        # prefer resources we can reach earlier; break ties by being farther in "contested distance"
        val = (do - ds) * 1000 - ds
        if (tx, ty) == (sx, sy):
            val = 10**12
        if val > best_val:
            best_val = val
            best_t = (tx, ty)

    if best_t is None:
        # no reachable resources: stay deterministic
        return [0, 0]

    tx, ty = best_t
    curd = distS[sx][sy]
    # choose neighbor that strictly decreases our distance; if none, choose minimal distance
    chosen = (0, 0)
    chosen_d = distS[sx][sy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = distS[nx][ny]
        if d < chosen_d or (d == chosen_d and (dx, dy) < chosen):
            chosen_d = d
            chosen = (dx, dy)
    return [int(chosen[0]), int(chosen[1])]