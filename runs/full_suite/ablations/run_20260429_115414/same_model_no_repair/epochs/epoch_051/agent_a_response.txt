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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        qx, qy = [start[0]], [start[1]]
        head = 0
        dist[start[0]][start[1]] = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
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

    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dself[rx][ry]
        do = dop[rx][ry]
        if ds < 0:
            continue
        if do < 0:
            key = (-ds, ds, rx, ry)
        else:
            if ds <= do:
                key = (-ds, 0, (do - ds), rx, ry)
            else:
                key = (ds, 1, (do - ds), rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        return [0, 0]

    tx, ty = best_res
    if sx == tx and sy == ty:
        return [0, 0]

    curd = dself[sx][sy]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = dself[nx][ny]
        if nd < 0:
            continue
        candidates.append((nd, dx, dy))
    if not candidates:
        return [0, 0]

    # Prefer strictly decreasing distance; then minimize next distance; then deterministic tie-break by move order.
    candidates.sort(key=lambda t: (0 if t[0] < curd else 1, t[0], moves.index((t[1], t[2]))))
    return [candidates[0][1], candidates[0][2]]