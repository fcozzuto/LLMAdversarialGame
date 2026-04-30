def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        qx = [x0]
        qy = [y0]
        dist[y0][x0] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_score = -10**18
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= 10**9:
            continue
        if d2 >= 10**9:
            score = 10**6 - d1
        else:
            score = (d2 - d1) * 1000 - d1 + (rx == sx and ry == sy) * 100000
        if score > best_score or (score == best_score and (best is None or (rx, ry) < best)):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    cur = myd[sy][sx]
    chosen = [0, 0]
    best_nd = myd[sy][sx]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = myd[ny][nx]
            if nd < best_nd or (nd == best_nd and (dx, dy) < tuple(chosen)):
                best_nd = nd
                chosen = [dx, dy]

    return chosen