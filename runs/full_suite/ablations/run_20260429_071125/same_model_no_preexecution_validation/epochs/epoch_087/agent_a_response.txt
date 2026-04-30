def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
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
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best_target = None
    best_score = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF:
            continue
        if do >= INF:
            val = 10**6 - ds
        else:
            val = (do - ds) * 1000 - ds
        if val > best_score:
            best_score = val
            best_target = (rx, ry)

    if best_target is None:
        tx, ty = sx, sy
    else:
        tx, ty = best_target

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds_next = dS[nx][ny]
        if ds_next >= INF:
            continue
        if best_target is None:
            val = -ds_next
        else:
            ds_t = dS[tx][ty]
            do_t = dO[tx][ty]
            do_next = dO[nx][ny]
            # Keep moving toward target; also prefer states where opponent is slower.
            val = -abs(ds_next - (ds_t - 1)) + (10**6 if do_next >= INF else (do_next - ds_next))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]