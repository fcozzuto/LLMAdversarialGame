def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not free(start[0], start[1]): return dist
        qx = [start[0]]; qy = [start[1]]; qi = 0
        dist[start[0]][start[1]] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    target = None
    best = None
    for rx, ry in resources:
        d1 = myd[rx][ry]; d2 = opd[rx][ry]
        if d1 >= 10**9: 
            continue
        opp_adv = (d2 - d1) if d2 < 10**9 else 10**6  # prefer denying when opponent is far
        key = (-opp_adv, d1, abs(rx - ox) + abs(ry - oy), rx, ry)
        if best is None or key < best:
            best = key; target = (rx, ry)

    if target is None:
        # Fallback: move toward opponent-blocking center line biased by who is closer overall
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = (cx, cy)
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                candidates.append((max(abs(nx - ox), abs(ny - oy)) * (1 if myd[sx][sy] <= opd[ox][oy] else 0) + abs(nx - tx) + abs(ny - ty), dx, dy))
        candidates.sort(key=lambda t: (t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]] if candidates else [0, 0]

    tx, ty = target
    curd = myd[sx][sy]
    # Prefer next step that strictly reduces distance; otherwise keep closest.
    bestmove = None
    bestkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): 
            continue
        d = myd[nx][ny]
        if d >= 10**9: 
            continue
        reduce = d - curd
        # tie-break deterministically: closer to target, then closer to opponent (to contest), then fixed order
        key = (0 if d < curd else 1, d, abs(nx - tx) + abs(ny - ty), abs