def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    if w != 8 or h != 8:
        pass

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0):
            dist[x0][y0] = 0
        elif inb(x0, y0):
            dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d0 = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and d0 < dist[nx][ny]:
                    dist[nx][ny] = d0
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs_dist((sx, sy))
    opd = bfs_dist((ox, oy))

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        if inb(sx + dx, sy):
            return [dx, 0]
        if inb(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md, od = myd[rx][ry], opd[rx][ry]
        score = (od - md, -md, rx, ry)  # race advantage, then closer
        if best is None or score > best[0]:
            best = (score, rx, ry)

    _, tx, ty = best
    cur_md = myd[sx][sy]
    # Choose move that minimizes our distance to target; deterministic tie-break
    best_mv, best_val = [0, 0], 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = myd[nx][ny]
        if val < best_val:
            best_val = val; best_mv = [dx, dy]
        elif val == best_val:
            # Prefer diagonal then x-axis then y-axis then stay; deterministic order by (dx,dy)
            if (dx, dy) in [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]:
                order = {(1, 1):0, (-1, 1):1, (1, -1):2, (-1, -1):3, (1, 0):4, (-1, 0):5, (0, 1):6, (0, -1):7, (0, 0):8}
                if order[(dx, dy)] < order[tuple(best_mv)]:
                    best_mv = [dx, dy]
    return best_mv