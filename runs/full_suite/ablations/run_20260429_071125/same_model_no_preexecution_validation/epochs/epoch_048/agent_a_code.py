def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    best = None
    best_key = None
    for tx, ty in resources:
        ds = distS[tx][ty]
        do = distO[tx][ty]
        if ds >= INF:
            continue
        # Prefer resources we can arrive earlier; otherwise, prefer closest with small lead.
        key = (0 if do > ds else 1, ds, (ds - do) if do < INF else 10**6, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    curd = distS[sx][sy]
    best_step = (0, 0)
    best_val = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Choose step that greedily decreases distance-to-target; break ties deterministically.
        v = distS[nx][ny] + (0 if nx == tx and ny == ty else 0)
        if v < best_val:
            best_val = v
            best_step = (dx, dy)
        elif v == best_val:
            if (dx, dy) < best_step:
                best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]