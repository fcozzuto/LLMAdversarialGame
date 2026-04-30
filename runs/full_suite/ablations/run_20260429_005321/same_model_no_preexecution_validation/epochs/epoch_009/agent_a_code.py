def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))
    res_set = set((r[0], r[1]) for r in resources)

    best = None; bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if our_dist[ny][nx] == INF:
            continue
        v = 0
        if (nx, ny) in res_set:
            v += 10**6
        # Favor resources we can reach earlier, and deny resources where we are behind.
        for rx, ry in res_set:
            d1 = our_dist[ry][rx]; d2 = opp_dist[ry][rx]
            if d1 == INF and d2 == INF:
                continue
            if (nx, ny) == (rx, ry):
                continue
            if d1 == INF:
                v -= 30 * (d2 if d2 != INF else 10)
            elif d2 == INF:
                v += 35 * (50 - d1)
            else:
                slack = d2 - d1
                v += (120 if slack > 0 else -90) * (abs(slack) + 1)
                v += 2 * (d2 - d1)
        # Small preference for reducing our distance to any remaining resource
        mind = INF
        for rx, ry in res_set:
            d = our_dist[ry][rx]
            if d < mind:
                mind = d
        if mind != INF:
            v -= 3 * our_dist[ny][nx]
        if v > bestv:
            bestv = v; best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]