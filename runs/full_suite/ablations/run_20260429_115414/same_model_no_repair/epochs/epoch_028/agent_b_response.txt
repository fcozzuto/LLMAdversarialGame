def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles_list)

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
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                    if nd < dist[ny][nx]:
                        dist[ny][nx] = nd
                        qx.append(nx)
                        qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_key = None
    for rx, ry in resources:
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obs:
            continue
        d1, d2 = myd[ry][rx], opd[ry][rx]
        if d1 >= INF:
            continue
        # Prefer resources where we are relatively closer than opponent; then closer to us; then toward center.
        key = (d2 - d1, -d1, -((rx - cx) ** 2 + (ry - cy) ** 2))
        if best_key is None or key > best_key:
            best_key, best = key, (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    curd = myd[sy][sx]
    if curd >= INF:
        # Fallback: step that avoids obstacles and moves toward target roughly.
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nd_my = myd[ny][nx]
        if nd_my >= INF:
            continue
        nd_op = opd[ny][nx] if (0 <= nx < w and 0 <= ny < h) else INF
        # Primary: decrease distance to target; Secondary: increase opponent's distance to target (relative blocking); Tertiary: center.
        key = (-nd_my, opd[ty][tx] - myd[ty][tx], -((nx - cx) ** 2 + (ny - cy) ** 2))
        # also ensure progress from current distance when possible
        if best_move_key is None or key > best_move_key:
            best_move_key, best_move = key, [dx, dy]

    return best_move