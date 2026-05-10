def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs_set = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs_set.add((int(o[0]), int(o[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = moves

    def bfs(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * H for _ in range(W)]
        if not (0 <= sx0 < W and 0 <= sy0 < H) or (sx0, sy0) in obs_set:
            return dist
        q = [(sx0, sy0)]
        dist[sx0][sy0] = 0
        for x, y in q:
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs_set and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist

    self_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = self_dist[rx][ry]
        od = opp_dist[rx][ry]
        if sd >= 10**9:
            continue
        key = (sd - od, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    cur_sd = self_dist[sx][sy]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H) or (nx, ny) in obs_set:
            continue
        nsd = self_dist[nx][ny]
        if nsd >= 10**9:
            continue
        nod = opp_dist[nx][ny]
        key = (nsd, nod, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    # If already optimal or movement blocked, stay still
    if best_move_key is None or self_dist[sx + best_move[0]][sy + best_move[1]] >= 10**9:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]