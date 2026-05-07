def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in blocked:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for (rx, ry) in resources:
        a = ds[rx][ry]
        b = do[rx][ry]
        if a >= 10**8:
            continue
        diff = b - a  # you arrive sooner => positive
        key = (-diff, ry, rx)  # first minimize -diff, deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # fallback: move toward center if no reachable resources
        tx, ty = (w // 2), (h // 2)
    else:
        tx, ty = best

    # choose step that minimizes distance to target (deterministic tie-break)
    curd = ds if best is not None else bfs((sx, sy))
    best_step = (0, 0)
    best_val = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        val = ds[nx][ny] + (abs(nx - tx) + abs(ny - ty)) * 0.001  # stable ordering
        if val < best_val:
            best_val = val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]