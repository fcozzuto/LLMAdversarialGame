def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(stx, sty):
        dist = [[INF] * h for _ in range(w)]
        if not free(stx, sty): return dist
        dist[stx][sty] = 0
        qx = [stx]; qy = [sty]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best = None
    best_key = -10**18
    for rx, ry in resources:
        d1, d2 = myd[rx][ry], opd[rx][ry]
        if d1 >= INF or d2 >= INF:
            continue
        # Prefer resources we can reach sooner than opponent; lightly penalize longer travel.
        key = (d2 - d1) * 1000 - d1
        if key > best_key:
            best_key = key
            best = (rx, ry)

    def step_toward(tx, ty):
        best_move = (0, 0)
        best_d = INF
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # Greedy by our distance to target if known; otherwise by Manhattan to target.
            d = myd[nx][ny]
            if tx is not None:
                d2 = abs(tx - nx) + abs(ty - ny)
                d = d * 10 + d2
            if d < best_d:
                best_d = d
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    if best is not None:
        return step_toward(best[0], best[1])

    # Fallback: move toward center or away from opponent if blocked.
    cx, cy = w // 2, h // 2
    mx = 0 if sx == cx else (1 if cx > sx else -1)
    my = 0 if sy == cy else (1 if cy > sy else -1)
    cand = (mx, my)
    if free(sx + cand[0], sy + cand[1]):
        return [int(cand[0]), int(cand[1])]

    # If center step blocked, pick any legal move that reduces distance to center.
    best_move = (0, 0); best_md = abs(sx - cx) + abs(sy - cy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        md = abs(nx - cx) + abs(ny - cy)
        if md < best_md:
            best_md = md
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]