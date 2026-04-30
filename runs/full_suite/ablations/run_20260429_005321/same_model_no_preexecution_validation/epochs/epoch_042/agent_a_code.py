def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9
    def inb(x,y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0,y0) or (x0,y0) in obstacles: return None
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx,ny) and (nx,ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None or not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx,ry) or (rx,ry) in obstacles:
            continue
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        if od >= INF:
            key = (0, md, -rx, -ry)
        else:
            # prefer resources we can reach earlier; otherwise deny by still going
            lead = od - md
            key = (1, -lead, md, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    curd = myd[sy][sx]
    # pick a legal neighbor that strictly decreases distance to target; otherwise head toward target by metric
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd < curd:
            candidates.append((nd, dx, dy))
    if candidates:
        candidates.sort()
        return [candidates[0][1], candidates[0][2]]

    # fallback: greedy metric toward target (Chebyshev)
    bestd = INF; bestmove = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx,ny) or (nx,ny) in obstacles:
            continue
        est = max(abs(tx - nx), abs(ty - ny))
        if est < bestd or (est == bestd and (dx,dy) < bestmove):
            bestd = est; bestmove = (dx, dy)
    return [bestmove[0], bestmove[1]]