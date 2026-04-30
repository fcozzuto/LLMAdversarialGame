def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_adv = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        adv = (do - ds) * 1000 - ds
        if adv > best_adv or (adv == best_adv and ds < (distS[int(best[0])][int(best[1])]) if best else False):
            best_adv = adv
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best[0], best[1]
    distT = bfs(tx, ty)
    cur_d = distT[sx][sy]
    best_step = (0, 0)
    best_nd = cur_d
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distT[nx][ny]
        if nd < best_nd or (nd == best_nd and (dx, dy) < best_step):
            best_nd = nd
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]