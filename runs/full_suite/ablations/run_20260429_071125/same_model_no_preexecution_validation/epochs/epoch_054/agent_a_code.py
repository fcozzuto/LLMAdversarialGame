def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    if resources:
        distO = bfs(ox, oy)
        best = None
        bestv = -10**18
        for tx, ty in resources:
            ds = distS[tx][ty]
            if ds >= INF: 
                continue
            do = distO[tx][ty]
            advantage = (do - ds) if do < INF else ds
            v = advantage - 0.15 * ds
            if v > bestv:
                bestv = v
                best = (tx, ty)
        if best is None:
            resources = []
        else:
            tx, ty = best
            best_move = [0, 0]
            best_mv = INF
            best_adv = -10**18
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny): 
                    continue
                d = distS[nx][ny]
                if d < INF:
                    adv = 0
                    if resources:
                        ds = distS[tx][ty]
                        # prefer reducing distance to chosen target; stronger if also improves relative position
                        adv = (distO[tx][ty] - d) if 'distO' in locals() else -d
                    keyd = d
                    keyadv = adv
                    if keyd < best_mv or (keyd == best_mv and keyadv > best_adv):
                        best_mv, best_adv = keyd, keyadv
                        best_move = [dx, dy]
            return best_move

    cx, cy = (w - 1) // 2, (h - 1) // 2
    target = (cx, cy) if not resources else (resources[0][0], resources[0][1])
    tx, ty = target
    # greedy toward target with obstacle avoidance
    best_move = [0, 0]
    best_d = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if d < best_d:
                best_d = d
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]