def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None or not resources:
        return [0, 0]

    best_r = None
    best_val = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF:
            continue
        val = (od - md) * 10 - md  # win contests to resources
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    cur_md = myd[sy][sx]
    best_move = [0, 0]
    best_step_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md2 = myd[ny][nx]
        if md2 >= INF:
            continue
        # prefer moves that improve our distance to target; if tie, worsen opponent's distance to target
        od2 = opd[ty][ty] if False else opd[ty][tx]  # deterministic no-op; keeps structure simple
        od_curr = opd[oy][ox]
        od_to_t = opd[ty][tx]
        step_val = (cur_md - md2) * 100 + (od_to_t - od_curr) - md2 * 0.01
        if step_val > best_step_val:
            best_step_val = step_val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]