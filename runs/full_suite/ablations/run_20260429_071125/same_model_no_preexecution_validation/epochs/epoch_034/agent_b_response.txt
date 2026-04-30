def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_r = None
    best_score = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF:
            continue
        if do >= INF:
            adv = 9999
        else:
            adv = do - ds  # positive if we are closer
        # Strongly prefer guaranteed/leading targets; then prefer shorter distances; small tie bias to current x
        score = 5 * adv - 0.2 * ds
        score += 0.01 * (rx - sx)
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    best_move = (0, 0)
    best_val = INF
    cur_ds = distS[sx][sy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        # choose move that reduces distance to target; break ties by improving advantage at target
        val = nds
        if nds < cur_ds or nds == cur_ds:
            do_tx = distO[tx][ty]
            ds_tx = distS[tx][ty]
            # approximate: prefer being closer to target immediately; stronger if we are already ahead
            adv = (do_tx - ds_tx) if do_tx < INF and ds_tx < INF else 0
            val = val - 0.1 * adv
        if val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]