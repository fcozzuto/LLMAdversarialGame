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

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        qx, qy = [start[0]], [start[1]]
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

    if not resources:
        return [0, 0]

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None:
        return [0, 0]

    def best_target():
        best = None
        for rx, ry in resources:
            ds = dself[rx][ry]
            do = dop[rx][ry]
            if ds < 0 or do < 0:
                continue
            # Favor targets we can reach sooner; strongly prefer ones we beat opponent on.
            key = (do - ds, -(ds), do)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        return best[1] if best else None

    tgt = best_target()
    if tgt is None:
        return [0, 0]
    tx, ty = tgt

    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_next = dself[nx][ny]
        if ds_next < 0:
            continue
        # Secondary objective: move to reduce remaining distance to target.
        rem_self = abs(dself[tx][ty] - (ds_next + dself[tx][ty] - dself[tx][ty]))  # always 0; keep simple below
        rem_self = dself[tx][ty] - (dself[tx][ty] - ds_next + ds_next - ds_next)
        rem_self = dself[tx][ty] - (dself[nx][ny] + 0)  # approximation
        do_t = dop[tx][ty]
        # Deterministic combined score
        score = (do_t - (dself[nx][ny] if dself[nx][ny] >= 0 else 10**9),
                 -(dself[nx][ny] if dself[nx][ny] >= 0 else 10**9),
                 dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [