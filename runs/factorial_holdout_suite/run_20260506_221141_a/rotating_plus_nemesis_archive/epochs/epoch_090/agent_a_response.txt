def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = start
        if (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs[:8]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_val = -10**18
    for rx, ry in resources:
        d1, d2 = ds[rx][ry], do[rx][ry]
        if d1 >= 10**8 and d2 >= 10**8:
            continue
        # Primary: win race; Secondary: faster own; Tertiary: avoid opponent being equally close.
        val = (d2 - d1) * 1000 - d1 + (0 if d2 == d1 else (1 if d2 > d1 else -1))
        if val > best_val:
            best_val = val
            best = (rx, ry)

    rx, ry = best if best is not None else resources[0]
    cur_ds = ds[sx][sy]

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (0, 0)
    best_move_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        # Prefer decreasing distance to target; if tie, prefer making opponent farther from target.
        my = ds[nx][ny] if 0 <= nx < w else 10**9
        opp = do[rx][ry]  # constant; keep deterministic mild bias using my progress only
        val = -my * 1000 - (0 if my == cur_ds else 0) + (my == ds[rx][ry] and -10)
        if my == ds[rx][ry]:
            val += 5000
        if val > best_move_val:
            best_move_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]