def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    def bfs_dist(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inb(sx0, sy0):
            return dist
        dist[sx0][sy0] = 0
        qx, qy = [sx0], [sy0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and d < dist[nx][ny]:
                        dist[nx][ny] = d
                        qx.append(nx)
                        qy.append(ny)
        return dist

    distS = bfs_dist((sx, sy))
    distO = bfs_dist((ox, oy))

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= 10**8 or do >= 10**8:
            continue
        adv = do - ds
        key = (adv, -ds, -abs(rx - sx) - abs(ry - sy), -rx - 3 * ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    if best is None:
        return [0, 0]

    _, tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((distS[nx][ny], abs(tx - nx) + abs(ty - ny), dx, dy))
    candidates.sort()
    return [candidates[0][2], candidates[0][3]]