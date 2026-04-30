def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obs = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def bfs(start):
        INF = 10**9
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd0 = bfs((sx, sy))
    opd0 = bfs((ox, oy))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        val = 0
        for rx, ry in resources:
            d1 = myd0[ry][rx]
            d2 = opd0[ry][rx]
            if d1 >= 10**9:
                continue
            # estimate using one-step: prefer targets we can approach faster next
            d1n = d1 + (-1 if abs(rx - nx) + abs(ry - ny) <= abs(rx - sx) + abs(ry - sy) else 0)
            gain = (d2 - d1n)
            if gain < 0:
                gain *= 0.5
            val += gain * 10 + (-(abs(rx - nx) + abs(ry - ny)))
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move