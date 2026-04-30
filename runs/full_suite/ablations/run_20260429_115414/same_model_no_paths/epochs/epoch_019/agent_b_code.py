def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs(startx, starty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if (startx, starty) in obstacles:
            return dist
        dist[startx][starty] = 0
        q = [(startx, starty)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                cur = max(abs(nx - ox), abs(ny - oy))
                if -cur > best[0]:
                    best = (-cur, dx, dy)
        return [best[1], best[2]]

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best_cell = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        a = opd[rx][ry] - myd[rx][ry]
        if a > best_adv:
            best_adv = a
            best_cell = (rx, ry)

    tx, ty = best_cell
    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myt = myd[tx][ty] - myd[nx][ny] if myd[nx][ny] < 10**9 else 10**9
        # Higher score if we get closer to target and keep advantage over opponent.
        cur_adv = opd[tx][ty] - myd[nx][ny]
        opp_step = opd[tx][ty]
        score = 1000 * cur_adv - myd[tx][ty] - opp_step + (-max(abs(nx - ox), abs(ny - oy)))
        if score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]