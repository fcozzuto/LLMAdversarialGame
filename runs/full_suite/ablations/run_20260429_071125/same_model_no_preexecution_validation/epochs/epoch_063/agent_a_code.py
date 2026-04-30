def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
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

    dself = bfs(sx, sy)
    doppo = bfs(ox, oy)

    best = None
    best_adv = -INF
    for p in resources:
        rx, ry = int(p[0]), int(p[1])
        ds, do = dself[rx][ry], doppo[rx][ry]
        if ds >= INF or do >= INF:
            continue
        adv = (do - ds) * 2 - ds * 0.15 + (ds == 0) * 1.0
        if adv > best_adv:
            best_adv = adv
            best = (rx, ry)

    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    curd = dself[tx][ty]
    if curd >= INF:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Move one step along best option by descending our distance-to-target.
    best_move = (0, 0)
    best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dself[nx][ny]
        # Prefer actions that reduce our distance to the chosen target; slight bias to deny opponent.
        my_to_target = dself[nx][ty]
        opp_to_target = doppo[ox][oy]  # placeholder base; overridden next line by chosen target
        opp_to_target = doppo[nx][ty] if doppo[nx][ty] < INF else INF
        if dself[nx][ty] >= INF:
            continue
        val = (-my_to_target) + (curd == my_to_target) * 0.1 + (0 if opp_to_target >= INF else (opp_to_target - my_to_target) * 0.5)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]