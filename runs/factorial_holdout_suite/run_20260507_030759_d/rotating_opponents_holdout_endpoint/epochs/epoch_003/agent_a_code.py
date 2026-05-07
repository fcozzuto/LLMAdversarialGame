def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        dist[sx0][sy0] = 0
        q = [(sx0, sy0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: 
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) not in obstacles and d < dist[nx][ny]:
                        dist[nx][ny] = d
                        q.append((nx, ny))
        return dist

    def best_move_towards(dist_map, tx, ty):
        # pick neighbor with strictly smallest dist; deterministic tie-break by dx,dy order
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                val = dist_map[nx][ny]
                if best is None or val < best[0] or (val == best[0] and (dx, dy) < best[1]):
                    best = (val, (dx, dy))
        return best[1] if best is not None else [0, 0]

    if not resources:
        return [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        myd = ds[rx][ry]
        opd = do[rx][ry]
        if myd >= 10**9 and opd >= 10**9:
            continue
        if myd < 10**9 and opd >= 10**9:
            s = (10**8, -myd, rx, ry)
        elif myd >= 10**9 and opd < 10**9:
            s = (-10**8, myd, -rx, -ry)
        else:
            # primary: who reaches first; secondary: reach sooner; tertiary: deterministic coords
            s = (opd - myd, -myd, -rx, -ry)
        if best is None or s > best[0]:
            best = (s, (rx, ry))

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    if ds[tx][ty] >= 10**9:
        # can't reach; move to minimize opponent advantage by heading toward any reachable resource
        target = min(resources, key=lambda r: ds[r[0]][r[1]] if ds[r[0]][r[1]] < 10**9 else 10**9)
        tx, ty = target
    return list(best_move_towards(ds, tx, ty))