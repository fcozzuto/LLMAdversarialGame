def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_adv = -INF
    best_sd = INF
    best_rx = best_ry = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        sd = ds[rx][ry]
        od = do[rx][ry]
        if sd >= INF:
            continue
        adv = od - sd  # want to be closer than opponent
        # tie-break deterministically toward smaller sd, then toward "forward" movement
        if adv > best_adv or (adv == best_adv and (sd < best_sd or (sd == best_sd and (rx + ry) % 2 == 0))):
            best_adv = adv
            best_sd = sd
            best = (rx, ry)
            best_rx, best_ry = rx, ry

    if best is None:
        return [0, 0]

    tx, ty = best_rx, best_ry
    # choose a move that decreases distance to target; if blocked, deterministic fallback
    curd = ds[tx][ty]
    best_move = (0, 0)
    best_nd = curd
    tie = 0
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nd = ds[nx][ny]  # not perfect, but monotone-ish via BFS distances
        # primary: reachability/closer-to-target by ds-from-self BFS:
        # use distance from new position to target via reusing ds by symmetry approximation:
        # Since ds is from self, we instead minimize ds[new] relative to current, and also prefer toward target direction.
        # Directional tie-break to avoid stalling.
        dir_score = (nx - sx) * (tx - sx) + (ny - sy) * (ty - sy)
        if nd < best_nd or (nd == best_nd and (dir_score > tie or (dir_score == tie and (dx, dy) == (0, 0) == False))):
            best_nd = nd
            best_move = (dx, dy)
            tie = dir_score

    # if the chosen move can't reduce our distance-to-target at all, directly approximate by stepping toward target
    if best_move == (0, 0):
        step_dx = 0 if tx == sx else (1 if tx > sx else -1)
        step_dy = 0 if ty == sy else (1 if ty