def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(src):
        sx0, sy0 = src
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        dist[sx0][sy0] = 0
        qx = [sx0]
        qy = [sy0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    qx.append(nx)
                    qy.append(ny)
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    def best_target():
        best = None
        for rx, ry in resources:
            my = ds[rx][ry]
            ot = do[rx][ry]
            if my >= 10**8 or ot >= 10**8:
                continue
            ahead = my - ot  # negative means we are closer
            key = (0 if ahead < 0 else 1, ahead, my, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1] if best is not None else resources[0]

    tx, ty = best_target()
    if ds[tx][ty] >= 10**8:
        return [0, 0]

    cur_d = ds[sx][sy]
    best_step = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nd = ds[nx][ny]
        if nd >= 10**8:
            continue
        # Prefer moving along decreasing shortest path distance to target; tie-break by better distance advantage over opponent.
        step_key = (0 if nd == cur_d - 1 else 1, nd, (nd - do[nx][ny]), abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or step_key < best_key:
            best_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]