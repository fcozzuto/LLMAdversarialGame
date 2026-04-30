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
        qx = [start[0]]
        qy = [start[1]]
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
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None:
        return [0, 0]

    best = None
    best_score = None
    for rx, ry in resources:
        ds = dself[rx][ry]
        do = dop[rx][ry]
        if ds == -1:
            continue
        if do == -1:
            key = (1, -ds, rx, ry)
        else:
            advantage = do - ds  # positive means we arrive earlier
            key = (0, -advantage, ds, rx, ry)
        # choose earlier with stronger advantage; deterministic tie-break by coords
        if best_score is None or key < best_score:
            best_score = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    rx, ry = best
    if (sx, sy) == (rx, ry):
        return [0, 0]

    curd = dself[rx][ry]
    best_next = (0, 0)
    best_c = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dself[nx][ny]
        if nd == -1:
            continue
        # move to reduce distance to target; secondary: maximize opponent delay if we can reach target
        opp_future = dop[rx][ry] if dop[rx][ry] != -1 else 0
        self_future = nd + (curd - dself[sx][sy])  # keeps target-consistent heuristic
        c = (abs((dself[nx][ny] + (curd - dself[sx][sy]))) - self_future, 0)
        # simpler deterministic ordering:
        c = (-((opp_future - (dself[nx][ny] + 0))), nd, nx, ny)
        if best_c is None or c < best_c:
            best_c = c
            best_next = (dx, dy)

    return [int(best_next[0]), int(best_next[1])]