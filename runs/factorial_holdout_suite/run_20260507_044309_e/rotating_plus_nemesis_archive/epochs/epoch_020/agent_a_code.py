def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_from(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in blocked:
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
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    dS = bfs_from((sx, sy))
    dO = bfs_from((ox, oy))

    best = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= 10**8:
            continue
        # Prefer resources we can reach strictly earlier; otherwise minimize disadvantage.
        key = (-(do - ds), ds, rx, ry)  # larger (ds-do) preferred; then smaller ds
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    cur_best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        nd = dS[nx][ny]
        if nd >= 10**8:
            continue
        # Move that best reduces self distance to target; tie-break by closer to target coordinates.
        k = (nd, abs(tx - nx) + abs(ty - ny), dx, dy)
        if cur_best is None or k < cur_best[0]:
            cur_best = (k, dx, dy)
    if cur_best is None:
        return [0, 0]
    return [int(cur_best[1]), int(cur_best[2])]