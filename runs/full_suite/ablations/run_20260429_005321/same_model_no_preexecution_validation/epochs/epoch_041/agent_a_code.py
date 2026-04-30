def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0,y0 = start
        if not inb(x0,y0) or (x0,y0) in obstacles: return None
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        qx=[x0]; qy=[y0]; qi=0
        while qi < len(qx):
            x=qx[qi]; y=qy[qi]; qi+=1
            nd = dist[y][x] + 1
            for dx,dy in dirs:
                nx,ny = x+dx, y+dy
                if inb(nx,ny) and (nx,ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx,sy)); opd = bfs((ox,oy))
    if myd is None or opd is None: return [0,0]
    if not resources: return [0,0]

    scored = []
    for r in resources:
        rx, ry = r[0], r[1]
        if not inb(rx,ry) or (rx,ry) in obstacles: 
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF: 
            continue
        # Prefer resources we can reach before opponent; otherwise still consider closest.
        val = (od - md) * 100 - md
        scored.append((val, md, od, rx, ry))
    if not scored: return [0,0]
    scored.sort(key=lambda t: (-t[0], t[1], t[2], t[3], t[4]))
    _, _, _, tx, ty = scored[0]

    best_move = (0,0)
    best = -10**18
    # Evaluate one-step moves with a deterministic tie-break.
    for dx,dy in dirs:
        nx, ny = sx+dx, sy+dy
        if not inb(nx,ny) or (nx,ny) in obstacles: 
            nx, ny = sx, sy
        my_dist = myd[ny][nx]
        opp_dist = opd[ny][nx]
        # Core: get closer to target. Secondary: keep opponent farther from our next position.
        v = (-my_dist) + (opp_dist) * 0.15
        # If target is reachable, add direct target pressure.
        t_md = myd[ty][tx] if myd[ty][tx] < INF else INF
        step_md = myd[ny][nx]
        v += -t_md * 0.01
        # Stronger pressure when target is competitive.
        v += (opd[ty][tx] - myd[ty][tx]) if myd[ty][tx] < INF else 0
        if (v > best) or (v == best and (dx,dy) < best_move):
            best = v
            best_move = (dx,dy)

    return [int(best_move[0]), int(best_move[1])]