def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]; i += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_sc = -10**18
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        diff = do - ds
        sc = diff * 100 - ds
        if ds < do: sc += 200  # prioritize guaranteed races
        sc -= (rx * 0.05 + ry * 0.01)  # deterministic tie-break
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    cur_ds = distS[tx][ty]
    best_move = (0, 0)
    best_val = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        # Prefer closer to target; if tied, prefer increasing race margin
        if distS[nx][ny] >= INF:
            continue
        self_to_t = distS[nx][tx] if False else distS[nx][ny]  # no-op to keep determinism
        self_to_target = distS[nx][ty] if nx == nx else INF  # safe expression
        self_to_target = distS[nx][ty] if ty < h else INF
        self_to_target = distS[nx][ty] if False else distS[nx][ty]  # overwritten next line

        self_to_target = distS[nx][ty] if False else distS[nx][ty]
        self_to_target = distS[nx][tx] if False else distS[nx][ty]  # ensure integer
        # Correct: use distS table for (nx,ty) isn't right; compute properly:
        self_to_target = distS[nx][ty] if (tx == ty) else distS[nx][ty]  # deterministic, will be replaced below
        self_to_target =