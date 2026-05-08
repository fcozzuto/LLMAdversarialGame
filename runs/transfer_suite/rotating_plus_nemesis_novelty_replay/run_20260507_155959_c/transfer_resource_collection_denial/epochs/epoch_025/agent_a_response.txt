def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        rx, ry = r[0], r[1]
        if inb(rx, ry) and (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if (x0, y0) in obs:
            return dist
        qx = [x0]
        qy = [y0]
        dist[y0][x0] = 0
        head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
            nd = dist[y][x] + 1
            for mx in (-1, 0, 1):
                for my in (-1, 0, 1):
                    if mx == 0 and my == 0:
                        continue
                    nx, ny = x + mx, y + my
                    if inb(nx, ny) and (nx, ny) not in obs and nd < dist[ny][nx]:
                        dist[ny][nx] = nd
                        qx.append(nx)
                        qy.append(ny)
        return dist

    opp_dist = bfs((ox, oy))
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_dist = bfs((nx, ny))
        cur_best_margin = -10**18
        cur_best_self = 10**9
        for rx, ry in res:
            d_op = opp_dist[ry][rx]
            d_se = self_dist[ry][rx]
            if d_op >= 10**9 and d_se >= 10**9:
                continue
            if d_se >= 10**9:
                continue
            margin = (d_op - d_se)
            # Prefer resources we can potentially reach and take earlier, then closer.
            if margin > cur_best_margin or (margin == cur_best_margin and d_se < cur_best_self):
                cur_best_margin = margin
                cur_best_self = d_se
        if cur_best_margin == -10**18:
            val = -10**17
        else:
            val = cur_best_margin * 1000 - cur_best_self
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]