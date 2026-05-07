def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(p) for p in (observation.get("resources") or [])]
    if w <= 0 or h <= 0:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not inb(sx, sy):
        return [0, 0]

    res = [p for p in resources if inb(p[0], p[1])]
    if not res:
        return [0, 0]

    INF = 10**9
    dist = [[INF] * w for _ in range(h)]
    q = [(sx, sy)]
    dist[sy][sx] = 0
    qi = 0
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while qi < len(q):
        x, y = q[qi]
        qi += 1
        nd = dist[y][x] + 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and nd < dist[ny][nx]:
                dist[ny][nx] = nd
                q.append((nx, ny))

    best = None
    bestd = INF
    for rx, ry in res:
        d = dist[ry][rx]
        if d < bestd:
            bestd = d
            best = (rx, ry)

    if best is None or bestd == INF:
        return [0, 0]

    tx, ty = best
    best_move = [0, 0]
    curd = INF
    for dx, dy in dirs + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and dist[ny][nx] < curd:
            curd = dist[ny][nx]
            best_move = [dx, dy]
    return best_move