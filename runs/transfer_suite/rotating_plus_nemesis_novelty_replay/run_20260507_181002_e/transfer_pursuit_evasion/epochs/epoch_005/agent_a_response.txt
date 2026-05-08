def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)] + [(0, 0)]

    INF = 10**9
    dist = [[INF] * h for _ in range(w)]
    qx = [ox]; qy = [oy]; dist[ox][oy] = 0; qi = 0
    while qi < len(qx):
        x = qx[qi]; y = qy[qi]; qi += 1
        nd = dist[x][y] + 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if free(nx, ny) and nd < dist[nx][ny]:
                dist[nx][ny] = nd
                qx.append(nx); qy.append(ny)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def corner_score(x, y):
        best = -1
        for cx, cy in corners:
            d = abs(x - cx) + abs(y - cy)
            if d > best: best = d
        return best

    best_move = [0, 0]
    best_val = INF if is_pursuer else -INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        d = dist[nx][ny]
        if d >= INF:
            continue
        c = corner_score(nx, ny)
        if is_pursuer:
            val = (d, -c, dx, dy)
            if val < (best_val, ):
                best_val = d; best_move = [dx, dy]
            elif d == best_val:
                if (-c, dx, dy) < (-(corner_score(sx + best_move[0], sy + best_move[1])), best_move[0], best_move[1]):
                    best_move = [dx, dy]
        else:
            val = (d, c, -dx, -dy)
            if d > best_val:
                best_val = d; best_move = [dx, dy]
            elif d == best_val:
                bc = corner_score(sx + best_move[0], sy + best_move[1])
                if (c, -dx, -dy) > (bc, -best_move[0], -best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]