def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_r = None
    best_key = None
    for rx, ry in resources:
        dS = distS[rx][ry]
        if dS >= INF:
            continue
        dO = distO[rx][ry]
        if dO >= INF:
            adv = 10**6
        else:
            adv = dO - dS
        key = (adv, -dS, - (rx + ry))  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    curd = distS[sx][sy]
    best_move = (0, 0)
    best_dist = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = distS[nx][ny]
        if d < best_dist:
            best_dist = d
            best_move = (dx, dy)

    # If already at target or stuck, stay
    if (sx, sy) == (tx, ty) or best_dist >= INF or curd == best_dist:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]