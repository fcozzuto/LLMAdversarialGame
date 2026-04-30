def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)
    if blocked(sx, sy):
        return [0, 0]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF] * w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_t = None
    best_s = -INF
    for rx, ry in resources:
        d1 = myd[ry][rx]
        if d1 >= INF: 
            continue
        d2 = opd[ry][rx] if (opd is not None) else INF
        if d2 >= INF:
            s = 2.0 * (1e6 - d1)  # strongly prefer unreachable-to-opponent
        else:
            s = (d2 - d1) * 10.0 - d1  # contest nearest
        if s > best_s:
            best_s = s; best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    curd = myd[sy][sx]
    best_move = [0, 0]
    best_v = -INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d_my = myd[ny][nx]
        if d_my >= INF:
            continue
        if (nx, ny) == (sx, sy) and curd == myd[ty][tx]:
            return [0, 0]
        d_op = opd[ny][tx] if (opd is not None and not blocked(nx, ny)) else INF
        if opd is None or d_op >= INF:
            v = -d_my
        else:
            # maximize chance to arrive before opponent and keep opponent farther from target
            v = (opd[ty][tx] - d_op) * 3.0 + (d_opd_my := (opd[ty][tx] - d_my)) * 2.0 - d_my
            # Above includes a tie-break component toward smaller my distance
        if v > best_v:
            best_v = v; best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]