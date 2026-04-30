def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_sc = -10**18
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        if od >= INF:
            sc = 1000000 - md
        else:
            sc = (od - md) * 2000 - md + (md == 0) * 5000
        if sc > best_sc:
            best_sc = sc
            best = (rx, ry)

    if best is None:
        # Fallback: drift toward nearest open cell to our "frontier" (opponent corner)
        tx, ty = (w - 1, 0) if (ox, oy) == (0, 0) else (ox, oy)
        cx, cy = tx, ty
        bestd = INF; best = (sx, sy)
        for dx, dy in dirs8:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and myd[ny][nx] < bestd:
                bestd = myd[ny][nx]; best = (nx, ny)
    rx, ry = best

    curd = myd[sy][sx]
    # Prefer move that reduces our distance to target; break ties toward opponent side
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy; dx = 0; dy = 0
        md = myd[ny][nx]
        if md >= INF:
            continue
        dist_gain = curd - md
        tie = -(abs((nx - ox)) + abs((ny - oy)))  # mild pressure toward opponent region
        val = dist_gain * 10000 + tie
        if md == 0:
            val += 200000
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]