def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def free(x,y): return inb(x,y) and (x,y) not in obstacles

    INF = 10**9
    def bfs(x0, y0):
        dist = [[INF]*h for _ in range(w)]
        if not free(x0,y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best = None
    best_score = -10**18
    for rx, ry in resources:
        d1, d2 = myd[rx][ry], opd[rx][ry]
        if d1 >= INF: 
            continue
        # Prefer resources I can arrive at earlier; break ties by closer-to-me and farther-from-opponent.
        score = (d2 - d1) * 1000 - d1 + (d2 if d2 < INF else 0)
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        # No reachable resources: drift toward opponent to contest area.
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Greedy one-step move toward (tx,ty) that also improves my distance.
    curd = myd[sx][sy]
    best_step = (0, 0)
    best_step_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        nd = myd[nx][ny]
        # Prefer smaller distance-to-target and smaller my BFS distance.
        step_score = (-nd) * 10 - max(abs(tx - nx), abs(ty - ny))
        if nd == curd and (dx,dy) != (0,0):
            step_score -= 1
        if step_score > best_step_score:
            best_step_score = step_score
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]