def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
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

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    best = None
    for rx, ry in sorted((int(p[0]), int(p[1])) for p in resources):
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Prefer resources where we can arrive earlier; else pick best "catch-up" vs opponent.
        score = (ds - do, ds, do, rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    if best is None:
        # Fallback: move toward opponent to avoid wasting turns.
        tx, ty = ox, oy
    else:
        tx, ty = best[1]

    # Choose the neighbor (including stay) that most reduces our distance-to-target.
    curd = distS[sx][sy]
    best_move = (0, 0)
    best_val = (curd, 0, sx, sy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = (distS[nx][ny], abs(nx - tx) + abs(ny - ty), nx, ny)
        if v < best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]