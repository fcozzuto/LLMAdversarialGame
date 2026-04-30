def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obst_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obst_list)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF:
            continue
        key = (-(do - ds), ds, rx, ry)  # favor making opponent farther than us; then closest; then stable
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is not None:
        tx, ty = best
        cur_ds = dS[sx][sy]
        best_move = (0, 0)
        best_cmp = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nds = dS[nx][ny]
            ndo = dO[nx][ny]
            if nds >= INF:
                continue
            # primary: reduce distance-to-target; secondary: improve advantage at next cell; tertiary deterministic
            cmp = ((nds - dS[tx][ty]), (ndo - nds), dx, dy)
            if best_cmp is None or cmp < best_cmp:
                best_cmp = cmp
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Fallback: move to increase Chebyshev distance from opponent while staying valid
    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    best_move = (0, 0)
    best_dist = -1
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        cd = cheb(nx, ny, ox, oy)
        if cd > best_dist