def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    env = observation.get("environment_name", "resource_collection")

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        INF = 10**9
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not inside(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    def step_toward(target):
        best = (10**9, None)
        tx, ty = target
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                d = abs(tx - nx) + abs(ty - ny)
                if (d, dx, dy) < best:
                    best = (d, (dx, dy))
        return best[1] if best[1] is not None else (0, 0)

    if env == "resource_collection" and resources:
        ds = bfs((sx, sy))
        do = bfs((ox, oy))
        # Choose resource maximizing (opponent_distance - self_distance): bigger is better
        # Tie-break deterministically by smaller self distance, then lexicographic coord.
        best_res = None
        best_key = (-10**9, 10**9, 10**9, 10**9)
        for (rx, ry) in resources:
            if not inside(rx, ry):
                continue
            ss = ds[rx][ry]
            oo = do[rx][ry]
            if ss >= 10**9 or oo >= 10**9:
                continue
            key = (oo - ss, ss, rx, ry)
            # max on first component, then min on others
            if (key[0] > best_key[0]) or (key[0] == best_key[0] and (key[1], key[2], key[3]) < (best_key[1], best_key[2], best_key[3])):
                best_key = (key[0], key[1], key[2], key[3])
                best_res = (rx, ry)
        if best_res is not None:
            dx, dy = step_toward(best_res)
            return [int(dx), int(dy)]

    # Fallback: move toward the safer corner based on opponent proximity
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target = None
    best = (-1, 10**9)
    for cx, cy in corners:
        if inside(cx, cy) or (cx, cy) == (sx, sy):
            d_opp = abs(cx - ox) + abs(cy - oy)
            d_self = abs(cx - sx) + abs(cy - sy)
            key = (d_opp, d_self)
            if key[0] > best[0] or (key[0] == best[0] and key[1] < best[1]):
                best = key
                target = (cx, cy)
    if target is None:
        return [0, 0]
    dx, dy = step_toward(target)
    return [int(dx), int(dy)]