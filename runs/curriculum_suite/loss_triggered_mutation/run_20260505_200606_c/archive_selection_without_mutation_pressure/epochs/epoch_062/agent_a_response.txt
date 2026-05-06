def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    obs = set(tuple(p) for p in observation.get("obstacles", []) or [])
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(src):
        inf = 10**9
        dist = [[inf] * w for _ in range(h)]
        x0, y0 = src
        if 0 <= x0 < w and 0 <= y0 < h and (x0, y0) not in obs:
            dist[y0][x0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        d1, d2 = ds[ry][rx], do[ry][rx]
        if d1 >= 10**8 and d2 >= 10**8:
            continue
        # Prefer resources we can secure (arrive no later). Tie-break by largest safety margin.
        # If neither can secure, pick the one where we are closer (race) and/or deny opponent.
        if d1 <= d2:
            key = (0, d1, -(d2 - d1), rx, ry)
        else:
            key = (1, d1 - d2, d2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best if best is not None else resources[0]

    cur_ds = ds[sy][sx]
    cur_do = do[sy][sx]
    best_step = (0, 0)
    best_step_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        nds = ds[ny][nx]
        ndo = do[ny][nx]
        # Drive toward target; also try to increase opponent's remaining advantage.
        # Strongly penalize moving away from target if we can.
        to_target = ds[ny][rx]
        opp_to_target = do[ny][rx]
        key = (to_target, nds - cur_ds, -(opp_to_target - to_target), nx, ny, ndo - cur_do)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (nx - sx, ny - sy)

    return [int(best_step[0]), int(best_step[1])]