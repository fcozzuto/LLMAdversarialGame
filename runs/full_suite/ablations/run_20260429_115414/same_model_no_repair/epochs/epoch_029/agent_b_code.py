def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return dist
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
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

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # Prefer resources I can reach sooner than the opponent (deterministic tie-break).
    best = None
    best_score = INF
    res_sorted = sorted(resources, key=lambda r: (r[0], r[1]))
    for rx, ry in res_sorted:
        if (rx, ry) in obs:
            continue
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        score = d1 - 0.9 * d2  # smaller is better
        if score < best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    cur = myd[sy][sx]
    # Move to a neighbor that keeps shortest-path progress toward target; tie-break by move order.
    best_step = (0, 0)
    best_dist = cur
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            if myd[ny][nx] < best_dist:
                best_dist = myd[ny][nx]
                best_step = (dx, dy)
            elif myd[ny][nx] == best_dist:
                if (dx, dy) < best_step:
                    best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]