def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obst = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(x0, y0):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obst:
                    continue
                if nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        # Escape to farthest corner from opponent, avoiding obstacles.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: abs(p[0] - ox) + abs(p[1] - oy))
        best = [0, 0]
        bestd = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd or bestd == -10**9:
                bestd = d
                best = [dx, dy]
        return best

    ds = bfs_dist(sx, sy)
    do = bfs_dist(ox, oy)

    best_cell = None
    best_key = None
    for rx, ry in resources:
        sdist = ds[rx][ry]
        odist = do[rx][ry]
        adv = odist - sdist  # higher => we win the race
        key = (adv, -sdist, odist)  # deterministic tie-breakers
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    rx, ry = best_cell
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        # Prefer moves that reduce our distance to target and keep us ahead vs opponent on that target.
        val = -ds[nx][ny] + (do[rx][ry] - ds[rx][ry])
        # Also nudge toward target to avoid dithering.
        val += -abs(nx - rx) - abs(ny - ry) * 0.001
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move