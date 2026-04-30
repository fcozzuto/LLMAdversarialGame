def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
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

    if not resources:
        best = (0, 0, INF)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = max(abs(nx - ox), abs(ny - oy))
                if d > best[2] or (d == best[2] and (dx, dy) < (best[0], best[1])):
                    best = (dx, dy, d)
        return [best[0], best[1]]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        dsi = ds[rx][ry]; doi = do[rx][ry]
        if dsi >= INF: 
            continue
        # Favor: resources we can reach sooner and that the opponent reaches later; tie-break by nearer to us.
        key = (doi - dsi, -dsi, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        return [0, 0]

    _, (tx, ty) = best[1][0], best[1]
    best_move = (0, 0, INF)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        # Move to reduce our remaining distance to target; lightly prefer moves that also increase opponent distance.
        my = ds[nx][ny]
        opp = do[nx][ny]
        score = (-(abs(tx - nx) + abs(ty - ny)), -my, opp)
        if best_move[2] == INF or score > (best_move[2], -best_move[1], best_move[0]):
            best_move = (dx, dy, score[0] if isinstance(score, tuple) else INF)
    # Simpler deterministic fallback from computed distances:
    best2 = (INF, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            d_to = max(abs(tx - nx), abs(ty - ny))
            d_my = ds[nx][ny]
            d_opp = do[nx][ny]
            key = (d_to, d_my, -d_opp, dx, dy)
            if key < (best2[0], 0, 0, 0, 0) or best2[1] == 0 and best2[0] == INF:
                best2 = (d_to, dx, dy)
                bestdx, bestdy = dx, dy
    return [bestdx, bestdy] if 'bestdx' in locals() else [0, 0]