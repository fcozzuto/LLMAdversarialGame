def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_t = None
    best_score = -INF
    best_my = INF

    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            score = 10**6 - ds
        else:
            score = (do - ds) * 100 - ds
        if score > best_score or (score == best_score and (ds < best_my or (ds == best_my and (tx, ty) < best_t))):
            best_score = score
            best_my = ds
            best_t = (tx, ty)

    if best_t is None:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    tx, ty = best_t
    ds_cur = distS[sx][sy]
    best_step = [0, 0]
    best_next = INF
    best_tiebreak = -INF

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny]
        if nd >= INF:
            continue
        # prioritize progress toward target; break ties by making opponent farther to that target
        if nd < best_next:
            best_next = nd
            best_step = [dx, dy]
            best_tiebreak = (distO[nx][ny] if distO[nx][ny] < INF else INF)
        elif nd == best_next:
            dko = distO[nx][ny] if distO[nx][ny] < INF else INF
            if dko > best_tiebreak:
                best_step = [dx, dy]
                best_tiebreak = dko
            elif dko == best_tiebreak:
                # deterministic tie-break
                if (dx, dy) < (best_step[0], best_step[1]):
                    best_step = [dx, dy]

    return best_step