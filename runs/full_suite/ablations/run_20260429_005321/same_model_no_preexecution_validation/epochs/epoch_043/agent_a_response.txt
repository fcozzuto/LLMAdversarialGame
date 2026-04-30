def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    INF = 10**9
    dirs8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    dirs9 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
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
    if myd is None or opd is None or not resources:
        return [0, 0]

    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF:
            continue
        # Prefer resources we can beat; tie-break closer-first, then deterministic by position.
        lead = od - md
        take_first = 1 if md <= od else 0
        key = (take_first, lead, -md, -(abs(rx - sx) + abs(ry - sy)), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry, md, od)
    if best_t is None:
        return [0, 0]

    rx, ry, md, od = best_t
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in dirs9:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        # Encourage moves that reduce distance to target; if already equal, prefer block (closer to target than opponent).
        my_to_t = nd
        op_to_t = opd[ry][rx]  # keep opponent target distance fixed for stability
        move_key = (-(my_to_t), (op_to_t - my_to_t), 0 if (dx == 0 and dy == 0) else 1, -abs(dx) - abs(dy), dx, dy)
        if best_move_key is None or move_key > best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]