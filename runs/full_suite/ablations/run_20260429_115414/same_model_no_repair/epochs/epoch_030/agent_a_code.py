def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return dist
        dist[y0][x0] = 0
        qx = [x0]
        qy = [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_target = None
    best_key = (-INF, INF)  # (opd-myd, -myd) maximized
    for rx, ry in resources:
        my_dist = myd[ry][rx]
        if my_dist >= INF:
            continue
        op_dist = opd[ry][rx]
        key0 = op_dist - my_dist
        key1 = -my_dist
        if key0 > best_key[0] or (key0 == best_key[0] and key1 > best_key[1]):
            best_key = (key0, key1)
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        my_dist_next = myd[ny][nx]
        if my_dist_next >= INF:
            continue
        op_dist_next = opd[ny][nx]
        contest = op_dist_next - my_dist_next
        manh_to_target = abs(tx - nx) + abs(ty - ny)
        val = contest * 1000 - manh_to_target * 10 - my_dist_next
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]