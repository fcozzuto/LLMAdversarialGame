def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF]*w for _ in range(h)]
        if not inb(x0,y0) or (x0,y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x+dx, y+dy
                if inb(nx,ny) and (nx,ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None
    best_score = -10**18
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        lead = od - md  # higher means I'm closer / opponent farther
        score = lead * 100 - md - (0 if od >= INF else od)
        # deterministic tie-break by coordinates
        if score > best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    if best is None:
        # no reachable resources: move to improve position vs opponent (increase distance)
        best_step = (0, 0); best_d = -10**18
        for dx, dy in dirs:
            nx, ny = sx+dx, sy+dy
            if not inb(nx,ny) or (nx,ny) in obstacles:
                continue
            d = abs(nx-ox) + abs(ny-oy)
            if d > best_d:
                best_d = d; best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    tx, ty = best
    curd = myd[ty][tx]
    # If already at target (or unreachable mismatch), stay
    if curd == 0:
        return [0, 0]

    best_step = (0, 0); best_next = myd[sy][sx]
    for dx, dy in dirs:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        nd = myd[ny][nx]
        # Prefer moving to a neighbor that decreases distance to target
        if myd[ty][tx] == myd[ny][tx]:
            # if equal, deterministic tie-break: closer to opponent avoidance
            d2 = abs(nx-ox) + abs(ny-oy)
            if best_step == (0,0) or d2 > (abs((sx+best_step[0])-ox)+abs((sy+best_step[1])-oy)):
                best_step = (dx, dy)
        if myd[ty][nx] < myd[ty][sx] or (myd[ty][nx] == myd[ty][sx] and nd < best_next):
            best_step = (dx, dy)
            best_next = nd

    # More robust: choose the move that minimizes distance from neighbor to target
    min_dist = myd[ty][sx]
    for dx, dy in dirs:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        dt = myd[ty][nx]
        if dt < min_dist or (dt == min_dist and (sx+dx, sy+dy) < (sx+best_step[0], sy+best_step[1])):
            min_dist = dt; best_step = (dx, dy)

    return [best_step[0], best_step[1]]