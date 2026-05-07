def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    if not resources:
        return [0, 0]

    def bfs(start):
        sx0, sy0 = start
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if 0 <= sx0 < w and 0 <= sy0 < h and (sx0, sy0) not in obstacles:
            dist[sx0][sy0] = 0
        q = [(sx0, sy0)]
        head = 0
        dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    my_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        md = my_dist[rx][ry]
        od = opp_dist[rx][ry]
        if md >= 10**8 or od >= 10**8:
            continue
        lead = md - od  # smaller => earlier (good)
        center_bias = abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0)
        key = (lead, md, center_bias)
        if best_key is None or key < best_key:
            best_key, best = key, (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    # Greedy step: choose neighbor with lowest my_dist towards target
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]
    best_step = (0, 0)
    best_d = my_dist[sx][sy]
    for dx, dy in dirs + [(0, 0)]:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            d = my_dist[nx][ny]
            if d < best_d:
                best_d = d
                best_step = (dx, dy)
            elif d == best_d:
                # deterministic tie-break: smaller angle toward target
                cur = abs((sx + dx) - tx) + abs((sy + dy) - ty)
                best_cur = abs(sx + best_step[0] - tx) + abs(sy + best_step[1] - ty)
                if cur < best_cur:
                    best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]