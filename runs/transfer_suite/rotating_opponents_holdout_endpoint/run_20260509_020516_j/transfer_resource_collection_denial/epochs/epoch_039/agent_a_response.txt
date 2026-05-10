def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def bfs(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if (sx0, sy0) in obstacles:
            return dist
        dist[sx0][sy0] = 0
        q = [(sx0, sy0)]
        head = 0
        neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in neigh:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        q.append((nx, ny))
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))

    def key(cell):
        tx, ty = cell
        sdist = sd[tx][ty]
        odist = od[tx][ty]
        # Prefer cells we can reach earlier; if contested, go to the one where we're less behind.
        return (sdist - odist, sdist, tx, ty)

    tx, ty = min(resources, key=key)
    if sd[tx][ty] >= 10**9:
        return [0, 0]

    neigh2 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    curd = sd[sx][sy]
    for dx, dy in neigh2:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d2 = sd[nx][ny]
            # Move along non-increasing distance; tie-break toward target direction deterministically.
            cand = (d2 - curd, abs((tx - nx)) + abs((ty - ny)), nx, ny)
            if best is None or cand < best:
                best = cand
                bx, by = nx, ny
                bdx, bdy = dx, dy

    return [int(bdx), int(bdy)]