def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def bfs(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if 0 <= sx0 < w and 0 <= sy0 < h and (sx0, sy0) not in obstacles:
            dist[sx0][sy0] = 0
        qx = [sx0]
        qy = [sy0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if d < dist[nx][ny]:
                        dist[nx][ny] = d
                        qx.append(nx)
                        qy.append(ny)
        return dist

    self_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    best = None
    best_rx = best_ry = None
    for rx, ry in resources:
        sd = self_dist[rx][ry]
        od = opp_dist[rx][ry]
        if sd >= 10**9 and od >= 10**9:
            continue
        key = (-(od - sd), sd, od, ry, rx)
        if best is None or key < best:
            best = key
            best_rx, best_ry = rx, ry

    if best_rx is None:
        return [0, 0]

    tx, ty = best_rx, best_ry
    curd = self_dist[sx][sy]
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            nd = self_dist[nx][ny]
            if nd >= 10**9:
                continue
            # Prefer moves that reduce distance to target; break ties by improving competitive edge.
            opp_edge = opp_dist[nx][ny] - nd
            key = (nd, -opp_edge, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
    if best_move == [0, 0] and self_dist[sx][sy] > curd:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]