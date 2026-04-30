def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(startx, starty):
        if not free(startx, starty):
            return [[INF] * h for _ in range(w)]
        dist = [[INF] * h for _ in range(w)]
        dist[startx][starty] = 0
        qx = [startx]
        qy = [starty]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    opd = bfs(ox, oy)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((dx, dy, nx, ny))
        else:
            candidates.append((dx, dy, sx, sy))

    best_key = None
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        myd = bfs(nx, ny)
        score = 0
        # Encourage capturing resources earlier than opponent; strongly avoid giving opponent advantage.
        for rx, ry in resources:
            d1 = myd[rx][ry]
            if d1 >= INF:
                continue
            d2 = opd[rx][ry]
            if d2 < INF:
                score += max(0, d2 - d1) * 10 - d1
            else:
                score += 5 - d1
        key = (score, -abs((ox - nx)) - abs((oy - ny)), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_score = score

    return [int(best_key[2]), int(best_key[3])]