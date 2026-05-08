def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = [tuple(r) for r in (observation.get("resources", []) or [])]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    def pick_target():
        if not resources:
            return (w - 1, h - 1) if sx < w // 2 else (0, 0)
        ds = bfs((sx, sy))
        do = bfs((ox, oy))
        best = None
        for rx, ry in resources:
            d1 = ds[rx][ry]
            d2 = do[rx][ry]
            if d1 >= 10**9:
                continue
            adv = d2 - d1  # positive => we are closer
            score = (adv, -d1, -rx, -ry)
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        if best is None:
            return (w - 1, h - 1) if sx < w // 2 else (0, 0)
        return best[1]

    tx, ty = pick_target()
    ds = bfs((sx, sy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = ds[sx][sy]
    best = (-(10**9), 0, 0)  # (improvement, -nx, -ny)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = ds[nx][ny]
        imp = curd - nd
        # Prefer moves that progress toward target distance; if equal, deterministic lexicographic
        tdist = abs(nx - tx) + abs(ny - ty)
        key = (imp, -tdist, -nx, -ny)
        if key > best:
            best = key
            best_dx, best_dy = dx, dy

    if not best:
        return [0, 0]
    return [best_dx, best_dy]