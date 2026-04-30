def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        qx = [start[0]]; qy = [start[1]]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None or not resources:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = dself[rx][ry]
        do = dop[rx][ry]
        if ds == -1 or do == -1:
            continue
        key = (do - ds, -ds)  # maximize advantage, then minimize our distance
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = dself[nx][ny]
        if ds_next == -1:
            continue
        # primary: get closer to target (via BFS); secondary: reduce opp's ability by not improving them
        opp_next = dop[nx][ny]
        val = (ds_next, opp_next if opp_next != -1 else 10**9, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]