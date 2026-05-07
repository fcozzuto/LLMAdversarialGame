def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def bfs_dist(start):
        sx0, sy0 = start
        if (sx0, sy0) in obstacles:
            return None
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        dist[sy0][sx0] = 0
        q = [(sx0, sy0)]
        qi = 0
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and d < dist[ny][nx]:
                    dist[ny][nx] = d
                    q.append((nx, ny))
        return dist

    myd = bfs_dist((sx, sy))
    opd = bfs_dist((ox, oy))
    if myd is None:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx] if opd is not None else 10**9
        if d1 >= 10**9:
            continue
        key = (d2 - d1, -d1)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    cur = myd[sy][sx]
    if cur >= 10**9:
        return [0, 0]

    candidates = []
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = myd[ny][nx]
            candidates.append((nd, dx, dy))
    candidates.sort(key=lambda z: (abs(best_key[1]) if False else 0, z[0]))
    chosen = None
    best_nd = 10**9
    for nd, dx, dy in candidates:
        if nd < best_nd:
            best_nd = nd
            chosen = (dx, dy)
    if chosen is None:
        return [0, 0]
    dx, dy = chosen
    return [int(dx), int(dy)]