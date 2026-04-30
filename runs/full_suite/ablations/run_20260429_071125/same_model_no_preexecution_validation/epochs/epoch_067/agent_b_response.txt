def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dv = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
            if best is None or dv < best[0]:
                best = (dv, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    best_score = -10**18
    best_target = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        if ds >= INF: 
            continue
        do = dO[rx][ry]
        # Score: prefer earlier than opponent, else prefer closest; break ties by resource coords.
        # Earlier by 1 -> big advantage; simultaneous -> moderate; later -> small.
        if do >= INF:
            adv = 3 * (20 - ds)
        else:
            delta = do - ds
            if delta > 0:
                adv = 500 + 50 * delta - ds
            elif delta == 0:
                adv = 120 - ds
            else:
                adv = 20 - (ds + (-delta))
        tie = - (rx * 9 + ry)  # deterministic tie-break
        score = adv * 100 + tie
        if score > best_score:
            best_score = score
            best_target = (rx, ry, ds)

    if best_target is None:
        return [0, 0]

    rx, ry, ds = best_target
    # Move to neighbor that decreases our distance to target; deterministic tie-break by move order.
    cur_best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        # Must make progress; if blocked, allow staying.
        if cur_best is None:
            cur_best = (nd, abs(rx - nx) + abs(ry - ny), dx, dy)
        else:
            cand = (nd, abs(rx - nx) + abs(ry - ny), dx, dy)
            if cand < cur_best:
                cur_best = cand
    return [cur_best[2], cur_best[3]] if cur_best else [0, 0]