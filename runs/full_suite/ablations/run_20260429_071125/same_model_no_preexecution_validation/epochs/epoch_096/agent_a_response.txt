def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Select a target resource to maximize score potential against opponent.
    if resources:
        best_score = -10**18
        tx, ty = sx, sy
        for rx, ry in resources:
            ds = dS[rx][ry]
            do = dO[rx][ry]
            if ds >= INF and do >= INF:
                continue
            # Prefer resources we can reach, and that we can contest (larger dO-dS).
            reachable = 0 if ds >= INF else 1
            if not reachable:
                score = -100000 + (do == INF)
            else:
                contest = (0 if do >= INF else (do - ds))
                score = contest * 1000 - ds
            if score > best_score:
                best_score = score
                tx, ty = rx, ry
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose move that improves toward target; break ties deterministically.
    best = (INF, -INF, 0, 0)  # (our_dist, -opp_dist, dx, dy) with lex tie via dx/dy order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our = dS[nx][ny] + dS[tx][ty]
        oppd = dO[nx][ny]
        # If opponent is closer to target than us, prefer moves that increase their distance to target.
        opp_to_target = dO[tx][ty]
        if opp_to_target < INF:
            opp_adv = oppd - (opp_to_target - our)
        else:
            opp_adv = oppd
        cand = (dS[tx][ty] + dS[nx][ny], -(opp_to_target if opp_to_target < INF else 10**6) - opp_adv, dx, dy)
        if cand < best:
            best = cand

    return [int(best[2]), int(best[3])]