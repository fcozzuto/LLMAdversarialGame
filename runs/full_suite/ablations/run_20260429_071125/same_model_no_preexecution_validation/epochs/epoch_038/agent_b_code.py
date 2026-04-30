def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_val = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        # Prefer resources we can reach, deny those opponent can also reach soon, and prefer earlier access
        # Deterministic tie-break by resource coordinate.
        val = (do - ds) * 10 - ds
        if do < ds:  # if opponent is closer, heavily penalize
            val -= 50
        if val > best_val or (val == best_val and (rx, ry) < (best[0], best[1]) if best else True):
            best_val = val
            best = (rx, ry)

    # If no reachable resources, drift toward opponent to block/contest
    if best is None:
        tx, ty = ox, oy
    else:
        tx, ty = best

    # Choose deterministic move that minimizes distance to target (and avoids obstacles implicitly)
    curd = distS[tx][ty] if best is not None else INF
    best_move = (0, 0)
    best_mval = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny] + (distO[nx][ny] * 0 if best is not None else 0)
        # primary: reduce distance-to-target, secondary: deterministic tie by move order and then opponent distance
        if best is not None:
            td = distS[nx][ny] + (distS[tx][ty] - distS[sx][sy])  # consistent monotonic proxy
            mval = distS[nx][ny] * 0 + (abs(nx - tx) + abs(ny - ty))
        else:
            mval = abs(nx - tx) + abs(ny - ty)
        # Also slightly prefer positions that are not worse for blocking opponent when contested
        if best is not None and distO[nx][ny] < INF:
            mval -= (distO[nx][ny] - distO[ox][oy]) * 0.001
        if mval < best_mval or (mval == best_mval and (dx, dy) < best_move):
            best_mval = mval
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]