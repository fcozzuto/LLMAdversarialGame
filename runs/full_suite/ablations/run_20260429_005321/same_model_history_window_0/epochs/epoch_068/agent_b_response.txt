def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        if 0 <= start[0] < w and 0 <= start[1] < h and start not in obstacles:
            dist[start[1]][start[0]] = 0
        q = [start] if dist[start[1]][start[0]] == 0 else []
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    dist_self = bfs((sx, sy))
    dist_opp = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        ds = dist_self[ry][rx]
        do = dist_opp[ry][rx]
        if ds >= 10**9:
            continue
        if do >= 10**9:
            score = (ds, -10**6)
        else:
            score = (ds, -(do - ds))
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    dist_to_target = bfs((tx, ty))
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        dt = dist_to_target[ny][nx]
        if dt >= 10**9:
            continue
        opp_dist = max(abs(nx - ox), abs(ny - oy))
        key = (dt, -opp_dist)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]