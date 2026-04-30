def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        inf = 10**9
        dist = [[inf] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        d1 = ds[rx][ry]
        d2 = do[rx][ry]
        if d1 >= 10**9:
            continue
        # Prefer targets where we're faster; otherwise pick farthest-advantage opportunities.
        key = (d2 - d1, -d1, -(abs(rx - ox) + abs(ry - oy)))
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        return [0, 0]

    tx, ty = best
    curd = ds[tx][ty]
    # Move deterministically toward target, avoiding worse self distance.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((ds[nx][ny], dx, dy))
    candidates.sort(key=lambda t: (t[0], abs((sx + t[1]) - tx) + abs((sy + t[2]) - ty), t[1], t[2]))
    for d, dx, dy in candidates:
        if d < curd:
            return [dx, dy]
    # Otherwise, pick the move that least increases distance.
    return [candidates[0][1], candidates[0][2]]