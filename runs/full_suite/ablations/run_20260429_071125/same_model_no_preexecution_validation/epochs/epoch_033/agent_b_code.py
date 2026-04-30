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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_r = None
    best_val = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF:
            continue
        # Prefer resources we can reach and where we are at least as close as opponent.
        # Use deterministic value to break ties.
        val = (do - ds) * 5 - ds
        if do < INF and do < ds:
            val -= 30  # strongly avoid "opponent-favored" targets unless no alternatives
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        # Fallback: move toward the best available cell by (lower dist to nearest resource), otherwise hold.
        best_step = (0, 0); best_step_val = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            step_val = -distS[nx][ny]
            if step_val > best_step_val:
                best_step_val = step_val; best_step = (dx, dy)
        return [int(best_step[0]), int(best_step[1])]

    tx, ty = best_r
    # Choose the valid move that most reduces our distance to the target.
    curd = distS[sx][sy]
    best_move = (0, 0)
    best_mval = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = distS[nx][ny]
        # Primary: smaller distance to target; Secondary: smaller opponent distance to target; Tertiary: tie-break by move order
        if d < INF:
            mval = (d, distO[nx][ty] if distO[nx][ty] < INF else INF)
        else:
            continue
        if mval < (best_mval, INF):
            best_mval = d
            best_move = (dx, dy)
        elif d == best_mval:
            # deterministic tie-break: prefer moves that also improve relative advantage at the target
            cur_adv = distO[sx][ty] - distS[sx][ty] if distO[sx][ty] < INF and distS[sx][ty] < INF else -