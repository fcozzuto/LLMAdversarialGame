def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy): return [0, 0]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    INF = 10**9

    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF] * w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources: return [0, 0]
    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None: return [0, 0]
    if opd is None:
        opd = [[INF] * w for _ in range(h)]

    best_t = None
    best_val = -10**18
    for rx, ry in resources:
        dme = myd[ry][rx]
        if dme >= INF: 
            continue
        dpo = opd[ry][rx]
        # Prefer resources we can reach earlier than opponent, then prefer nearer.
        val = (dpo - dme) * 4 - dme
        if val > best_val:
            best_val = val
            best_t = (rx, ry)
    if best_t is None: return [0, 0]

    tx, ty = best_t
    curd = myd[sy][sx]
    # Take a neighbor that strictly improves distance to target; otherwise fall back to best distance.
    best_step = [0, 0]
    best_step_dist = INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        nd = myd[ny][nx]
        if nd < best_step_dist:
            best_step_dist = nd
            best_step = [dx, dy]
    # If already at target or no improvement possible, prefer staying.
    if (sx, sy) == (tx, ty): return [0, 0]
    if best_step == [0, 0]: return [0, 0]
    return best_step