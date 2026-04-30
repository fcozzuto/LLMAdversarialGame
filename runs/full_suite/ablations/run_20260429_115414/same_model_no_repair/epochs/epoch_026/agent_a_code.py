def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_r = None
    best_key = None
    for rx, ry in resources:
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        d1 = myd[ry][rx]
        if d1 >= INF:
            continue
        d2 = opd[ry][rx]
        # Prefer targets we can reach sooner than opponent (maximize margin), then shorter our distance, then deterministic position.
        margin = d2 - d1
        key = (margin, -d1, -((rx * 31 + ry) % 997))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r
    curd = myd[sy][sx]
    # Choose a legal move that leads along decreasing distance to target; tie-break by increasing opponent distance.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd >= INF:
            continue
        od = opd[ny][nx]  # opponent distance not directly to target, but tie-break for safety/space
        key = (-(nd - curd), -nd, od, dx, dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]