def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(src):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = src
        if (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Choose resource that maximizes our advantage; if close, pick nearer one.
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = ds[rx][ry]
        d2 = do[rx][ry]
        if d1 >= 10**9:
            continue
        if d2 >= 10**9:
            key = (10**8, -d1)
        else:
            adv = d2 - d1
            key = (adv, -d1)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best
    # Move to keep shortest distance to target; if tie, increase opponent distance to same target.
    best_move = (0, 0)
    cur = ds[sx][sy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        if ds[nx][ny] > cur + 1:
            continue
        key = (-ds[nx][ny], do[nx][ty] if do[nx][ty] < 10**9 else -10**9, -abs(ox - nx) - abs(oy - ny))
        if best_move == (0, 0) or key > best_move[0]:
            best_move = (key, dx, dy)
    if isinstance(best_move[0], tuple):
        return [best_move[1], best_move[2]]
    return [0, 0]