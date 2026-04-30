def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF]*h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    if resources:
        best_sc = -10**18
        best_target = None
        for rx, ry in resources:
            if not valid(rx, ry): 
                continue
            dS = distS[rx][ry]; dO = distO[rx][ry]
            if dS >= INF and dO >= INF:
                continue
            if dS >= INF:
                sc = -10**12 + (dO if dO < INF else 0)
            elif dO >= INF:
                sc = 10**11 - dS
            else:
                sc = (dO - dS) * 1000 - dS * 3 + (dS == dO) * 5
            sc -= cheb(sx, sy, rx, ry) * 0.01
            if sc > best_sc:
                best_sc, best_target = sc, (rx, ry)

        if best_target is not None:
            tx, ty = best_target
            best_d = INF
            best_move = (0, 0)
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                d = distS[nx][ny]
                if d < best_d:
                    best_d = d
                    best_move = (dx, dy)
                elif d == best_d:
                    if cheb(nx, ny, tx, ty) < cheb(sx + best_move[0], sy + best_move[1], tx, ty):
                        best_move = (dx, dy)
            return [best_move[0], best_move[1]]

    # Fallback: move toward center if possible while preferring to increase distance from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = (-10**18, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = cheb(nx, ny, ox, oy) * 20 - cheb(nx, ny, cx, cy) * 2
        if score > best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]