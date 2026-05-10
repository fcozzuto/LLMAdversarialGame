def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    INF = 10**9

    # BFS from self for shortest distances with obstacles (8-neighbor).
    dist = [[INF] * h for _ in range(w)]
    if (sx, sy) not in obstacles:
        qx, qy = [sx], [sy]
        dist[sx][sy] = 0
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            d = dist[x][y] + 1
            for dx, dy in dirs[:-1] + [dirs[-1]]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    qx.append(nx); qy.append(ny)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Choose resource maximizing "how much earlier I can arrive" over opponent.
    best = None
    for rx, ry in resources:
        my_d = dist[rx][ry]
        if my_d >= INF:
            continue
        opp_d = cheb(ox, oy, rx, ry)
        # Primary: arrive earlier margin; Secondary: smaller my_d; Tertiary: lexicographic.
        key = (opp_d - my_d, -my_d, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, my_d)
    if best is None:
        # Fallback: direct cheb to some resource.
        rx, ry = resources[0]
        for r in resources[1:]:
            if cheb(sx, sy, r[0], r[1]) < cheb(sx, sy, rx, ry):
                rx, ry = r[0], r[1]
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
        return [dx, dy]

    _, rx, ry, my_d = best

    # Pick move that minimizes own distance to target, with deterministic tie-break favoring closer to target.
    best_move = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        nd = dist[nx][ny]
        # Prefer smaller dist; then smaller resulting dist to target (dist to target from new pos via cheb approximation)
        # and then tie-break by dx,dy ordering.
        est = cheb(nx, ny, rx, ry)
        key = (nd, est, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])
    return best_move[1]